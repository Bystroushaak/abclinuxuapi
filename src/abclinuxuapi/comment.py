#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import copy
from collections import namedtuple

import dhtmlparser
from repoze.lru import lru_cache

from shared import first
from shared import url_context
from shared import date_izolator
from shared import parse_timestamp


# Functions & classes =========================================================
class Comment(object):
    """
    Comment representation.

    Note:
        For registered users, the :attr:`username` property contains `real`
        username, which may differ from what you see, but this allows you to
        identify the user.

        This is because registered users can (and do) change their `visible`
        usernames anytime they want.

    Attributes:
        url (str): Absolute URL of the comment.
        text (str): Fulltext of the comment.
        timestamp (int): Date of the publication as timestamp.
        username (str): Username of the poster.
        registered (bool): Was the user registered?
        censored (bool): Is the comment censored? If so, you will need
                 additional parsing of the comment, which is not yet
                 implemented.
        responses (list): List of :class:`Comment` instances responding to this
                  comment.
        response_to (obj): Reference to :class:`Comment` to which you are
                    responding. ``None`` in cases where the object is at the
                    top of the comment tree.
    """
    def __init__(self):
        self._id = None

        self.url = None
        self.text = None
        self.timestamp = None

        self.username = None
        self.registered = False
        self.censored = False

        self.responses = []
        self.response_to = None

    @property
    @lru_cache(1)
    def id(self):
        """
        Returns:
            str: Identification of the comment.
        """
        # http://abclinuxu.cz/blog/msk/2016/8/hlada-sa-linux-embedded-vyvojar
        # doesn't have urls in comments, for fucks sake
        if self.url:
            return self.url.split("#")[-1]

        return self._id

    @staticmethod
    def _izolate_timestamp(head_tag):
        text_elements = head_tag.find(None, fn=lambda x: not x.isTag())

        text_clusters = [str(x).splitlines() for x in text_elements]
        lines = sum(text_clusters, [])  # flattern the list

        return parse_timestamp(lines)

    @staticmethod
    def _izolate_username(head_tag):
        user_tag = head_tag.find(
            "a",
            fn=lambda x: x.params.get("href", "").startswith("/lide/")
        )

        if user_tag:
            user_link = first(user_tag).params["href"]

            # /lide/manasekp -> manasekp
            real_username = user_link.split("/")[2]

            return real_username, True  # registered

        # parse unregistered username from unstructured HTML like:
        #         10.2. 21:53
        #
        #       Tomáškova máma

        str_repr = dhtmlparser.removeTags(head_tag.getContent())

        # remove blank lines
        lines = [x.strip() for x in str_repr.splitlines() if x.strip()]

        # izolate line with time
        line_with_time = first(date_izolator(lines))

        # pick line next to line with time
        username = lines[lines.index(line_with_time) + 1]

        def clean_username(username):
            if username == "Rozbalit":  # no username was found
                return ""

            return username.strip()

        return clean_username(username), False  # unregistered

    @staticmethod
    def _parse_url(head_tag):
        comment_id = head_tag.params["id"]

        # parse full link from
        # <a href="/blog/EditDiscussion/400959;jsessionid=kufis2spplnh6gu671mxq
        # e2j?action=add&amp;dizId=210591&amp;threadId=9">Odpovědět</a>
        response_tag = head_tag.find(
            "a",
            fn=lambda x: x.getContent() == "Odpovědět"
        )

        try:
            response_link = first(response_tag).params["href"]
        except StopIteration:
            return None

        # /blog/EditDiscussion/400959;jsessii... -> /blog/EditDiscussion/400959
        response_link = response_link.split(";")[0]

        # /blog/EditDiscussion/400959?action=a.. -> /blog/EditDiscussion/400959
        response_link = response_link.split("?")[0]

        # /blog/EditDiscussion/400959 -> 400959
        blog_id = first(
            token
            for token in response_link.split("/")
            if token.isdigit()
        )

        return url_context("/blog/show/%s#%s" % (blog_id, comment_id))

    @staticmethod
    def _response_to(head_tag):
        response_to_tag = head_tag.find(
            "a",
            fn=lambda x: x.getContent() == "Výše"
        )

        if not response_to_tag:
            return None

        # <a href="#2" title="...">Výše</a> -> #2
        response_to_link = first(response_to_tag).params["href"]

        # #2 -> 2
        return response_to_link.split("#")[-1]

    @staticmethod
    def _parse_text(body_tag):
        censored = False
        text_tag = body_tag.find("div", {"class": "ds_text"})

        if not text_tag:
            censored = True
            text_tag = body_tag.find("div", {"class": "cenzura"})

        if not text_tag:
            raise ValueError("Can't find comment body!")

        return first(text_tag).getContent().strip(), censored

    @staticmethod
    def _from_head_and_body(head_tag, body_tag, uid=None):
        """
        uid is optional, because it's used only at pages without comment links.
        See http://abclinuxu.cz/blog/msk/2016/8/hlada-sa-linux-embedded-vyvojar
        for details.
        """
        c = Comment()

        # fill object
        c._id = uid
        c.url = Comment._parse_url(head_tag)
        c.text, c.censored = Comment._parse_text(body_tag)
        c.response_to = Comment._response_to(head_tag)
        c.timestamp = Comment._izolate_timestamp(head_tag)
        c.username, c.registered = Comment._izolate_username(head_tag)

        return c

    @staticmethod
    def comments_from_html(html):
        """
        Parse comments in `html`, return list of connected :class:`Comment`
        instances.

        Args:
            html (str): Webpage for parsing.

        Returns:
            list: List of :class:`Comment` instances linked also into trees \
                  using :attr:`response_to` and :attr:`responses` properties.
        """
        def cut_dom_to_area_of_interest(html):
            dom = html

            # make sure, that you don't modify `html` parameter
            if not isinstance(html, dhtmlparser.HTMLElement):
                dom = dhtmlparser.parseString(html)
            else:
                dom = copy.deepcopy(dom)
            dhtmlparser.makeDoubleLinked(dom)

            # comments are not stored in hierarchical structure, but in somehow
            # flat-nested lists

            # locate end of article
            ds_toolbox = dom.find("div", {"class": "ds_toolbox"})

            if not ds_toolbox:
                raise ValueError("Couldn't locate ds_toolbox!")

            ds_toolbox = first(ds_toolbox)
            dom = ds_toolbox.parent

            # ged rid of everything until end of the article
            while dom.childs[0] != ds_toolbox:
                dom.childs.pop(0)

            dom.childs.pop(0)

            return dom

        # pick all header divs
        def header_div_class(item):
            """
            Identify header dicts. Sometimes there is class="ds_hlavicka" and
            sometimes there is class="ds_hlavicka ds_hlavicka_me".
            """
            class_descr = item.params.get("class", "")

            return class_descr.startswith("ds_hlavicka")

        def id_from_comment_div(comment_div):
            # <div id="comment3"> -> 3
            id_str = comment_div.parent.params.get("id")

            # see http://abclinuxu.cz/blog/Mostly_IMDB/2008/6/radeon-hd-4850-a\
            # -tak-vubec#17 for details
            if not id_str:
                id_str = comment_div.parent.parent.params.get("id")

            if not id_str:
                id_str = comment_div.parent.parent.parent.params["id"]

            return id_str.replace("comment", "")

        def comment_or_censored(tag):
            return tag.params.get("class", "") in ("ds_text", "cenzura")

        def parse_comments(dom, head_dict):
            IdBodyPair = namedtuple("IdBodyPairs", ["uid", "comment_div"])

            # I need to use the ID two times in the next pass, thats why
            id_body_pairs = (
                IdBodyPair(
                    uid=id_from_comment_div(comment_div),
                    comment_div=comment_div,
                )
                for comment_div in dom.find("div", fn=comment_or_censored)
            )

            return [
                Comment._from_head_and_body(
                    head_dict[uid],
                    comment_div,
                    uid,
                )
                for uid, comment_div in id_body_pairs
            ]

        dom = cut_dom_to_area_of_interest(html)

        head_dict = {
            head_div.params["id"]: head_div
            for head_div in dom.find("div", fn=header_div_class)
        }

        comment_list = parse_comments(dom, head_dict)

        # {id: comment}
        comment_dict = {
            comment.id: comment
            for comment in comment_list
        }

        # link comments into tree
        for comment in comment_list:
            if comment.response_to:
                comment.response_to = comment_dict[comment.response_to]
                comment.response_to.responses.append(comment)

        return comment_list

    def __repr__(self):
        return "Comment(username=%s, id=%s)" % (self.username, self.id)
