#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from collections import namedtuple


#= Variables ==================================================================
#= Functions & objects ========================================================
class Rating(namedtuple("Rating", ["rating", "base"])):
    pass


class Blogpost(namedtuple("Blogpost", ["title",
                                       "comments_n",
                                       "rel_link",
                                       "timestamp",
                                       "link",
                                       "rating",
                                       "intro"])):
    def get_full_text(self):
        raise NotImplementedError("Not implemented yet.")

    def get_comments(self):
        raise NotImplementedError("Not implemented yet.")

    def edit(self):
        raise NotImplementedError("Not implemented yet.")
