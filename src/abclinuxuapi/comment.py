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
from shared import parse_timestamp


# Functions & classes =========================================================
class Comment(object):
    def __init__(self):
        self.url = None
        self.text = None
        self.timestamp = None

        self.username = None
        self.registered_user = False

        self.responses = []  #: Reference to all response comments
        self.response_to = None  #: Reference to parent comment

    @property
    def comment_id(self):
        return self.url.split("#")[-1]

    @staticmethod
    def _izolate_timestamp(head_tag):
        text_elements = head_tag.find(None, fn=lambda x: not x.isTag())

        text_clusters = [str(x).splitlines() for x in text_elements]
        lines = sum(text_clusters, [])  # flattern the list

        return parse_timestamp(lines)

    @staticmethod
    def _izolate_username(head_tag):
        user_tag = head_tag.find("a", {"href": "/lide/manasekp"})

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
        line_with_time = first(x for x in lines if ":" in x and "." in x)

        # pick line next to line with time
        username = lines[lines.index(line_with_time) + 1]

        return username.strip(), False  # unregistered

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

        # /blog/EditDiscussion/400959 -> 400959
        blog_id = first(
            token
            for token in response_link.split("/")
            if token.isdigit()
        )

        return url_context("/blog/show/%s#%s" % (blog_id, comment_id))

    @staticmethod
    def _from_head_and_body(head_tag, body_tag):
        c = Comment()
        c.timestamp = Comment._izolate_timestamp(head_tag)
        c.username, c.registered_user = Comment._izolate_username(head_tag)

        print head_tag
        # print body_tag

        assert False

    @staticmethod
    def comments_from_html(html):
        dom = html

        if isinstance(html, basestring):
            dom = dhtmlparser.parseString(html)
        else:
            dom = copy.deepcopy(dom)

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

        # comments are not stored in hierarchical structure, but in somehow
        # flat-nested lists

        # pick all header divs
        head_dict = {
            head_div.params["id"]: head_div
            for head_div in dom.find("div", {"class": "ds_hlavicka"})
        }

        def id_from_comment_div(comment_div):
            # <div id="comment3"> -> 3
            id_str = comment_div.parent.params["id"]

            return id_str.replace("comment", "")

        # go thru all comment lists
        comment_list = [
            Comment._from_head_and_body(
                head_dict[id_from_comment_div(comment_div)],
                comment_div
            )
            for comment_div in dom.find("div", {"class": "ds_text"})
        ]


