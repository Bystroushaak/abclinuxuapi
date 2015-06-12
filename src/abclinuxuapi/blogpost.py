#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import copy
from collections import namedtuple

import dhtmlparser

from shared import first
from shared import download
from shared import url_context
from shared import parse_timestamp
from shared import date_to_timestamp
from comment import Comment


# Functions & objects =========================================================
class Rating(namedtuple("Rating", ["rating", "base"])):
    """
    Container holding informations about rating.

    Attributes:
        rating (int): Percentual rating of the blogpost.
        base (int): How many people voted.
    """
    def __repr__(self):
        return "%s(%d%%@%d)" % (
            self.__class__.__name__,
            self.rating,
            self.base
        )


class Tag(str):
    """
    Each blog may have many tags. This is container for informations about each
    tag.

    Attributes:
        name (str): Name of the tag.
        url (str): URL to the informations about tag.
    """
    def __new__(self, name, *args, **kwargs):
        return super(Tag, self).__new__(self, name)

    def __init__(self, name, url=None):
        super(Tag, self).__init__(name)

        self.name = name
        self.url = url


class Blogpost(object):
    """
    Informations about blogposts.

    Attributes:
        url (str): Absolute URL of the blogpost.
        title (str): Tile of the blogpost.
        intro (str): Perex. This is parsed only when returned from
                     :class:`User`.
        text (str): Full text of the blogpost.
        tags (list): List of :class:`Tag` objects.
        rating (obj): :class:`Rating` object with informations about rating.
        has_tux (bool): Does this blog have a tux? Only good blogs get tux.
        comments (list): List of :class:`.Comment` objects. Not used until
                 :meth:`.pull` is called, or `lazy` parameter of
                 :meth:`__init__` is set to ``True``.
        comments_n (int): Number of comments. This information is in some cases
                   known before the blog is parsed, just from perex.
        readed (int): How many times was the blog readed?
        object_ts (int): Timestamp of the creation of this object.
        created_ts (int): Timestamp of the creation of the blogpost.
        last_modified_ts (int): Timestamp of the last modification of blogpost.
    """
    def __init__(self, url, lazy=True, **kwargs):
        """
        Args:
            url (str): Url of the blogpost.
            lazy (bool, default True): True == don't call :meth:`pull` right
                 now.
        """
        self.url = url

        self.title = None
        self.intro = None
        self.text = None

        self.tags = None
        self.rating = None
        self.has_tux = False
        self.comments = []
        self.comments_n = -1
        self.readed = None

        self.object_ts = time.time()
        self.created_ts = None
        self.last_modified_ts = None

        # those are used for caching to speed up parsing
        self._dom = None
        self._content_tag = None

        # read parameters from kwargs
        for key, val in kwargs.iteritems():
            if key not in self.__dict__:
                raise TypeError("Unknown parameter `%s`!" % key)

            if key.startswith("_"):
                raise ValueError("You can't set protected/private properties!")

            self.__dict__[key] = val

        if not lazy:
            self.pull()

    @staticmethod
    def _parse_intro(blog, meta, title_tag):
        """
        Parse intro from the `meta` HTML part.
        """
        intro = blog.getContent().replace(str(meta), "")
        intro = intro.replace(str(title_tag), "")

        signature = blog.find("div", {"class": "signature"})
        if signature:
            intro = intro.replace(str(signature[0]), "")

        return dhtmlparser.removeTags(intro.strip()).strip()

    @staticmethod
    def _parse_comments_n(meta):
        """
        Parse number of comments under the blogpost.

        Args:
            meta (str): Meta html from the blogpost body.

        Returns:
            int: Number of comments.
        """
        comments = meta.find("a")[-1].getContent()
        comments = comments.split("&nbsp;")[1]

        return int(comments)

    @staticmethod
    def _parse_rating_from_preview(meta):
        """
        Parse rating of the blogpost.

        Args:
            meta (str): Meta html from the blogpost body.

        Returns:
            Rating: :class:`.Rating` object.
        """
        rating = filter(
            lambda x: "Hodnocení:" in x,
            str(meta).splitlines()
        )

        if rating:
            rating = rating[0].strip().replace("(", "")
            rating = rating.split("&nbsp;")

            return Rating(int(rating[1]), int(rating[3]))

    @staticmethod
    def from_html(html, lazy=True):
        """
        Convert HTML string to :class:`Blogpost` instance.

        Args:
            html (str): Input data.
            lazy (bool, default True): Be lazy (don't pull data by yourself
                 from the site). Call :meth:`pull` for active download of all
                 required informations.

        Returns:
            obj: :class:`Blogpost` instance.
        """
        if not isinstance(html, dhtmlparser.HTMLElement):
            html = dhtmlparser.parseString(html)
            dhtmlparser.makeDoubleLinked(html)

        # support for legacy blogs
        title_tag = html.find("h2", {"class": "st_nadpis"})
        if title_tag:
            title_tag = first(title_tag)
            rel_link = first(title_tag.find("a")).params["href"]
            link = url_context(rel_link)
        else:
            title_tag = first(html.find("h2"))
            link = first(html.find("link", {"rel": "canonical"}))
            link = link.params["href"]

        title = dhtmlparser.removeTags(title_tag).strip()

        # get meta
        meta = html.find("p", {"class": "meta-vypis"})[0]

        blog = Blogpost(url=link, lazy=lazy)

        if lazy:
            blog.title = title
            blog.intro = Blogpost._parse_intro(html, meta, title_tag)
            blog.rating = Blogpost._parse_rating_from_preview(meta)
            blog.created_ts = parse_timestamp(meta)
            blog.comments_n = Blogpost._parse_comments_n(meta)

        return blog

    def _parse_title(self):
        assert self._dom

        title_tag = self._dom.find("title")

        if not title_tag:
            return

        self.title = first(title_tag).getContent()

    def _parse_content_tag(self):
        assert self._dom

        if self._content_tag:
            return self._content_tag

        content_tags = self._dom.find("div", {"class": "st", "id": "st"})
        if not content_tags:
            raise ValueError("Can't find content - is this really blogpost?")

        self._content_tag = first(content_tags)

        if not self._content_tag.isOpeningTag():
            self._content_tag = self._content_tag.parent

        return self._content_tag

    def _parse_text(self):
        content_tag = copy.deepcopy(self._parse_content_tag())

        # this shit is not structured in tree, so the parsing is little bit
        # hard
        h2_tag = first(content_tag.find("h2"))
        rating_tag = first(content_tag.find("div", {"class": "rating"}))

        # throw everything until the h2_tag
        h2_parent = h2_tag.parent
        while h2_parent.childs[0] != h2_tag:
            h2_parent.childs.pop(0)

        # throw everything after the rating_tag
        rating_parent = rating_tag.parent
        while rating_parent.childs[-1] != rating_tag:
            rating_parent.childs.pop()

        # throw also the rating
        rating_parent.childs.pop()

        meta_vypis_tag = content_tag.find("p", {"class": "meta-vypis"})
        if meta_vypis_tag:
            content_tag.removeChild(meta_vypis_tag, end_tag_too=True)

        self.text = content_tag.getContent()

    def _parse_tags(self):
        tag_tags = self._parse_content_tag().find("div", {"class": "tag-box"})

        if not tag_tags:
            self.tags = []
            return

        self.tags = [
            Tag(
                tag.getContent(),
                url=url_context(tag.params["href"])
            )
            for tag in first(tag_tags).find("a")
            if tag.params.get("href", "").startswith("/stitky/")
        ]

    def _parse_rating(self):
        content = self._parse_content_tag()
        rating_tags = content.find("div", {"class": "rating"})

        if not rating_tags:
            return

        # <span> with voting info
        voting_spans = first(rating_tags).find("span")

        if not voting_spans:
            return

        voting_span = first(voting_spans)

        rating = voting_span.getContent()
        base = voting_span.params.get("title", "0")

        self.rating = Rating(
            rating=int(rating.split()[0]),
            base=int(base.split()[-1]),
        )

    def _parse_meta(self):
        content = self._parse_content_tag()
        meta_vypis_tags = content.find("p", {"class": "meta-vypis"})

        if not meta_vypis_tags:
            return

        meta_vypis_tag = first(meta_vypis_tags)
        has_tux_tags = meta_vypis_tag.find("img", {"class": "blog_digest"})

        if has_tux_tags:
            self.has_tux = True

        # get clean string - another thing which is not semantic at all
        lines = dhtmlparser.removeTags(meta_vypis_tag)

        self.created_ts = parse_timestamp(lines)

        # rest will be picked one by one
        lines = lines.strip().splitlines()

        # parse last modification time
        modified_ts_line = [x for x in lines if "poslední úprava:" in x]
        if modified_ts_line:
            date_string = first(modified_ts_line).split(": ")[-1]
            self.last_modified_ts = date_to_timestamp(date_string)

        # parse number of reads
        reads_line = [x for x in lines if "Přečteno:" in x]
        if reads_line:
            reads = first(reads_line).split(":")[-1].split("&")[0]
            self.readed = int(reads)

    def pull(self):
        """
        Download page with blogpost. Parse text, comments and everything else.

        Until this is called, following attributes are not known/parsed:

            - :attr:`text`
            - :attr:`tags`
            - :attr:`has_tux`
            - :attr:`comments`
            - :attr:`last_modified_ts`
        """
        data = download(url=self.url)

        # this is because of fucks who forgot to close elements like in this
        # blogpost: https://www.abclinuxu.cz/blog/EmentuX/2005/10/all-in-one
        blog_data, comments_data = data.split('<p class="page_tools">')

        self._dom = dhtmlparser.parseString(blog_data)
        self._content_tag = None
        dhtmlparser.makeDoubleLinked(self._dom)

        self._parse_title()
        self._parse_text()
        self._parse_tags()
        self._parse_rating()
        self._parse_meta()

        self.comments = Comment.comments_from_html(comments_data)
        self.comments_n = len(self.comments)

        # memory cleanup - this saves a LOT of memory
        self._dom = None
        self._content_tag = None

    def get_image_urls(self):
        """
        Get list of links to all images used in this blog.

        Returns:
            list: List of str containing absolute URL of the image.
        """
        image_links = (
            image_tag.params["src"]
            for image_tag in dhtmlparser.parseString(self.text).find("img")
            if "src" in image_tag.params
        )

        def remote_link(link):
            return link.startswith("http://") or link.startswith("https://")

        return [
            link if remote_link(link) else url_context(link)
            for link in image_links
        ]

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.title)
