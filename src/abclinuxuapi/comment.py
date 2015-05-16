#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import copy

import dhtmlparser

from shared import first


# Functions & classes =========================================================
class Comment(object):
    def __init__(self):
        self.url = None
        self.text = None
        self.poster = None
        self.poster_name = None
        self.timestamp = None

    @staticmethod
    def _from_head_and_body(head_tag, body_tag):
        pass

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

        # ged rid of everything until end of article
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
