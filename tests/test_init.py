#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import abclinuxuapi


# Tests =======================================================================
def test_iter_blogposts():
    blogs = [blog for blog in abclinuxuapi.iter_blogposts(end=0)]

    assert len(blogs) == 25
    assert blogs[0].created_ts > 0
    assert blogs[-1].created_ts > 0


def test_first_blog_page():
    blogs = abclinuxuapi.first_blog_page()

    assert len(blogs) == 25
    assert blogs[0].created_ts > 0
    assert blogs[-1].created_ts > 0


def test_next_blog_url():
    page_gen = abclinuxuapi._next_blog_url()

    assert next(page_gen) == "https://www.abclinuxu.cz/blog/?from=0"
    assert next(page_gen) == "https://www.abclinuxu.cz/blog/?from=25"

    assert next(abclinuxuapi._next_blog_url(4)).endswith("u.cz/blog/?from=100")
