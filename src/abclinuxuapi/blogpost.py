#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import copy
from urlparse import urljoin
from collections import namedtuple

import dhtmlparser

import shared
from shared import first
from shared import url_context
from shared import parse_timestamp
from shared import date_to_timestamp
from comment import Comment


# Functions & objects =========================================================
class Rating(namedtuple("Rating", ["rating", "base"])):
    pass


class Tag(str):
    def __new__(self, name, *args, **kwargs):
        return super(Tag, self).__new__(self, name)

    def __init__(self, name, url=None):
        super(Tag, self).__init__(name)

        self.name = name
        self.url = url


class Blogpost(object):
    def __init__(self, url, lazy=True, **kwargs):
        self.url = url

        self.title = None
        self.intro = None
        self.text = None

        self.tags = None
        self.rating = None
        self.has_tux = False
        self.comments = None
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
    def from_html(html):
        title_tag = first(html.find("h2", {"class": "st_nadpis"}))
        rel_link = first(title_tag.find("a")).params["href"]

        link = url_context(rel_link)
        title = dhtmlparser.removeTags(title_tag).strip()

        # get meta
        meta = html.find("p", {"class": "meta-vypis"})[0]

        blog = Blogpost(url=link, lazy=True)

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

        content_tags = self._dom.match(
            ["div", {"class": "obal"}],
            ["div", {"class": "st", "id": "st"}]
        )

        if not content_tags:
            raise ValueError("Can't find content - is this really blogpost?")

        return first(content_tags)

    def _parse_text(self):
        content_tag = copy.deepcopy(self._parse_content_tag())

        # this shit is not structured in tree, so the parsing is little bit
        # hard
        h2_tag = first(content_tag.find("h2"))
        rating_tag = first(content_tag.find("div", {"class": "rating"}))

        # throw everything to the h2_tag
        while content_tag.childs[0] != h2_tag:
            content_tag.childs.pop(0)

        # throw everything after the rating_tag
        while content_tag.childs[-1] != rating_tag:
            content_tag.childs.pop()

        # throw also the rating
        content_tag.childs.pop()

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
        data = shared.download(url=self.url)

        self._dom = dhtmlparser.parseString(data)
        self._content_tag = None

        self._parse_title()
        self._parse_text()
        self._parse_tags()
        self._parse_rating()
        self._parse_meta()

        self.comments = Comment.comments_from_html(self._dom)
        self.comments_n = len(self.comments)

    def edit(self):
        raise NotImplementedError("Not implemented yet.")

    def get_images(self):
        pass