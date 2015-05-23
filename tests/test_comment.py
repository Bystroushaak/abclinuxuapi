#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import dhtmlparser

from abclinuxuapi import Comment


# Fixtures ====================================================================


# Tests =======================================================================
def test_izolate_timestamp():
    timestamp_str = """<div class="ds_hlavicka" id="9">
        10.2. 21:53

               Tomáškova máma

    """
    ts = Comment._izolate_timestamp(
        dhtmlparser.parseString(timestamp_str)
    )
    assert ts == 1423601580

    timestamp_str = """    <div class="ds_hlavicka" id="9">
        <div class="ds_reseni" style="display:none">
        </div>


        11.2. 15:21

<a href="/lide/manasekp">manasekp</a>             | skóre: 27
             | blog: <a href="/blog/manasekp">manasekp</a>
             | Brno

        <br>
    """
    ts = Comment._izolate_timestamp(
        dhtmlparser.parseString(timestamp_str)
    )
    assert ts == 1423664460
