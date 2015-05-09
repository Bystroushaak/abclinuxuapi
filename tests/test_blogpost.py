#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import abclinuxuapi


# Fixtures ====================================================================
@pytest.fixture
def bp_url():
    return "http://www.abclinuxu.cz/blog/bystroushaak/2015/2/bolest-proxy"


@pytest.fixture
def bpost():
    return abclinuxuapi.Blogpost(bp_url(), lazy=False)


# Tests =======================================================================
def test_constructor(bp_url):
    bp = abclinuxuapi.Blogpost(bp_url)

    assert bp.url == bp_url
    assert bp.title is None
    assert bp.intro is None
    assert bp.text is None
    assert bp.rating is None
    assert bp.comments is None
    assert bp.comments_n == -1
    assert bp.created_ts is None
    assert bp.last_modified_ts is None
    assert bp.object_ts > 0


def test_constructor_multi_params(bp_url):
    bp = abclinuxuapi.Blogpost(
        url=bp_url,
        title="title",
        intro="intro",
        text="text",
        rating="rating",
        comments="comments",
        comments_n="comments_n",
        created_ts="created_ts",
        last_modified_ts="last_modified_ts",
        object_ts="object_ts"
    )

    assert bp.url == bp_url
    assert bp.title == "title"
    assert bp.intro == "intro"
    assert bp.text == "text"
    assert bp.rating == "rating"
    assert bp.comments == "comments"
    assert bp.comments_n == "comments_n"
    assert bp.created_ts == "created_ts"
    assert bp.last_modified_ts == "last_modified_ts"
    assert bp.object_ts == "object_ts"


def test_constructor_wrong_params(bp_url):
    with pytest.raises(TypeError):
        bp = abclinuxuapi.Blogpost(bp_url, azgabash=True)


def test_get_title(bpost):
    bpost.pull()

    assert bpost.title == "Bolest proxy"


def test_get_text(bpost):
    bpost.pull()

    assert bpost.text.startswith("<h2>Bolest proxy</h2>")
    assert "Written in CherryTree" in bpost.text
    assert "bystrousak:" in bpost.text
