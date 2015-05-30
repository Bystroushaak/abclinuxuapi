#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import copy

import dhtmlparser

from shared import first
from shared import url_context
from shared import date_izolator
from shared import parse_timestamp


# Functions & classes =========================================================
class Comment(object):
    def __init__(self):
        self.url = None
        self.text = None
        self.timestamp = None

        self.username = None
        self.registered = False  # was the user registered?
        self.censored = False

        self.responses = []  #: Reference to all response comments
        self.response_to = None  #: Reference to parent comment

    @property
    def id(self):
        return self.url.split("#")[-1]

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
        response_link = first(response_tag).params["href"]

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

        return first(text_tag).getContent(), censored

    @staticmethod
    def _from_head_and_body(head_tag, body_tag):
        c = Comment()

        # fill object
        c.url = Comment._parse_url(head_tag)
        c.text, c.censored = Comment._parse_text(body_tag)
        c.response_to = Comment._response_to(head_tag)
        c.timestamp = Comment._izolate_timestamp(head_tag)
        c.username, c.registered = Comment._izolate_username(head_tag)

        return c

    @staticmethod
    def comments_from_html(html):
        dom = html

        # make sure, that you don't modify `html` attribute
        if isinstance(html, basestring):
            dom = dhtmlparser.parseString(html)
        else:
            dom = copy.deepcopy(dom)

        # comments are not stored in hierarchical structure, but in somehow
        # flat-nested lists

        # pick the content tag
        dom = dom.find("div", {"class": "st", "id": "st"})
        dom = first(dom)
        dhtmlparser.makeDoubleLinked(dom)

        # locate end of article
        ds_toolbox = dom.find("div", {"class": "ds_toolbox"})

        if not ds_toolbox:
            raise ValueError("Couldn't locate ds_toolbox!")

        # ged rid of everything until end of the article
        while dom.childs[0] != first(ds_toolbox):
            dom.childs.pop(0)

        dom.childs.pop(0)

        # pick all header divs
        def header_div_class(item):
            """
            Identify header dicts. Sometimes there is class="ds_hlavicka" and
            sometimes there is class="ds_hlavicka ds_hlavicka_me".
            """
            class_descr = item.params.get("class", "")

            return class_descr.startswith("ds_hlavicka")

        head_dict = {
            head_div.params["id"]: head_div
            for head_div in dom.find("div", fn=header_div_class)
        }

        def id_from_comment_div(comment_div):
            # <div id="comment3"> -> 3
            id_str = comment_div.parent.params["id"]

            return id_str.replace("comment", "")

        def comment_or_censored(tag):
            return tag.params.get("class", "") in ("ds_text", "cenzura")

        # parse list of all comments on the page
        comment_list = [
            Comment._from_head_and_body(
                head_dict[id_from_comment_div(comment_div)],
                comment_div
            )
            for comment_div in dom.find("div", fn=comment_or_censored)
        ]

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
