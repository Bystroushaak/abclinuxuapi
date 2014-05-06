#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from collections import namedtuple


#= Variables ==================================================================
#= Functions & objects ========================================================
class Concept(namedtuple("Concept", ["title",
                                     "rel_link"])):
    def get_full_text(self):
        raise NotImplementedError("Not implemented yet.")

    def edit(self):
        raise NotImplementedError("Not implemented yet.")

    def add_picture(self, fn, data):
        raise NotImplementedError("Not implemented yet.")

    def remove(self):
        raise NotImplementedError("Not implemented yet.")
