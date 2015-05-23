#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import copy

import dhtmlparser

from shared import first
from shared import parse_timestamp


# Functions & classes =========================================================
class Comment(object):
    def __init__(self):
        self.url = None
        self.text = None
        self.poster_id = None
        self.poster_name = None
        self.timestamp = None

        self.response_to = None  #: Reference to parent comment
        self.responses = []  #: Reference to all response comments

    @staticmethod
    def _izolate_timestamp(head_tag):
        text_elements = head_tag.find(None, fn=lambda x: not x.isTag())

        text_clusters = [str(x).splitlines() for x in text_elements]
        lines = sum(text_clusters, [])  # flattern the list

        return parse_timestamp(lines)

    @staticmethod
    def _from_head_and_body(head_tag, body_tag):
        def izolate_name(head_tag):
            pass

        print head_tag
        print Comment._izolate_timestamp(head_tag)
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


