#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os.path
import pytest

import abclinuxuapi
from abclinuxuapi import shared


# Fixtures ====================================================================
@pytest.fixture
def bp_url():
    return "http://www.abclinuxu.cz/blog/bystroushaak/2015/2/bolest-proxy"


@pytest.fixture
def do_that_fucking_monkey_patch(monkeypatch):
    def mock_download(*args, **kwargs):
        fn = os.path.join(os.path.dirname(__file__), "mock_data/blogpost.html")

        with open(fn) as f:
            return f.read()

    monkeypatch.setattr(abclinuxuapi.blogpost, "download", mock_download)


def setup_module(do_that_fucking_monkey_patch):
    """
    It is not possiblel to import monkeypatch from pytest. You have to use it
    as fixture.
    """


BPOST = abclinuxuapi.Blogpost(bp_url(), lazy=False)

@pytest.fixture
def bpost():
    """
    This may seem a little bit crazy, but this speeds up the testing 6x.

    I don't need new object for each test.
    """
    return BPOST


# Tests =======================================================================
def test_constructor(bp_url):
    bp = abclinuxuapi.Blogpost(bp_url)

    assert bp.url == bp_url
    assert bp.title is None
    assert bp.intro is None
    assert bp.text is None
    assert bp.rating is None
    assert bp.comments == []
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
    assert bpost.title == "Bolest proxy"


def test_get_text(bpost):
    assert bpost.text.startswith("<h2>Bolest proxy</h2>")
    assert "Written in CherryTree" in bpost.text
    assert "bystrousak:" in bpost.text


def test_Tag():
    tag = abclinuxuapi.Tag("hello", url="http://..")

    assert tag == "hello"
    assert tag.url == "http://.."


def test_get_tags(bpost):
    assert bpost.tags
    assert "proxy" in bpost.tags


def test_get_rating(bpost):
    assert bpost.rating
    assert bpost.rating.rating == 100
    assert bpost.rating.base == 15


def test_meta_parsing(bpost):
    assert bpost.has_tux
    assert bpost.created_ts == 1423587660.0
    assert bpost.last_modified_ts >= 1423591140.0
    assert bpost.readed >= 1451


def test_get_image_urls(bpost):
    assert bpost.get_image_urls()
    assert bpost.get_image_urls()[0] == (
        "https://www.abclinuxu.cz/images/screenshots/0/9/"
        "210590-bolest-proxy-6017333664768008869.png"
    )
