#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time

import dhtmlparser as _dhtmlparser  # don't want this at package level

from user import User
from blogpost import Tag
from comment import Comment
from blogpost import Blogpost

import shared as _shared


# Functions & classes =========================================================
def _next_blog_url(start=0):
    """
    Args:
        start (int, default 0): Start at this page.

    Yields:
        str: Another url for blog listing.
    """
    for i in xrange(1000000):
        if i < start:
            continue

        yield _shared.url_context("/blog/?from=%d" % (i * 25))


def _should_continue(dom):
    """
    Detect pagination at the bottom of the bloglist page.

    Returns:
        bool: True if there is another page with list of blogposts.
    """
    paginators = dom.find(
        "a",
        fn=lambda x: x.params.get("href", "").startswith("/blog/?from=")
    )

    next_tags = [x for x in paginators if x.getContent() == "Starší zápisy"]

    return bool(next_tags)


def _remove_crap_from_bloglist(data):
    """
    Clean crap, get just content. This speeds up parsing.

    Args:
        data (str): Content of the bloglist page.

    Returns:
        str: `data` without crap.
    """
    # clean crap, get just content
    data = data.split(
        '<div class="s_nadpis linkbox_nadpis">Píšeme jinde</div>'
    )[0]
    data = data.split('<div class="st" id="st">')[1]

    # some blogs have openning comment in perex, which fucks ups bloglist
    # - this will close comments that goes over bloglist
    data = data.replace(
        '<div class="signature">',
        '<!-- --><div class="signature">'
    )

    return data


def iter_blogposts(start=0, end=None, lazy=True):
    """
    Iterate over blogs. Based at bloglist.

    Args:
        start (int, default 0): Start at this page.
        end (int, default None): End at this page.
        lazy (bool, default True): Initialize :class:`.Blogpost` objects only
             with informations from listings. Don't download full text and
             comments.

    Yields:
        obj: :class:`.Blogpost` objects.
    """
    for cnt, url in enumerate(_next_blog_url(start)):
        data = _shared.download(url)

        data = _remove_crap_from_bloglist(data)

        # parse basic info about all blogs at page
        dom = _dhtmlparser.parseString(data)
        for bcnt, blog in enumerate(dom.findB("div", {"class": "cl"})):
            yield Blogpost.from_html(blog, lazy=lazy)

            # every page has 25 blogposts, but somethimes I am getting more
            if bcnt >= 24:
                break

        # detect end of pagination at the bottom
        if not _should_continue(dom):
            break

        if end is not None and cnt >= end:
            break


def first_blog_page(lazy=True):
    """
    Return content of the first blogpost page.

    Args:
        lazy (bool, default True): Do not download full blog information.

    Returns:
        list: 25 :class:`.Blogpost` objects.
    """
    return list(iter_blogposts(end=0, lazy=lazy))


_search_cache = {}
def _binary_search(low, high, test_fn):
    def cached_test_fn(number):
        if number in _search_cache:
            return _search_cache[number]

        result = test_fn(number)
        _search_cache[number] = result

        return result

    if cached_test_fn(high):
        return high

    center = int((low + high) / 2)

    if cached_test_fn(center):
        return _binary_search(center + 1, high, cached_test_fn)
    else:
        return _binary_search(low, center - 1, cached_test_fn)


def number_of_blog_pages(progress_fn=None):
    """
    Find number of blog pages in listing. Multiply by 25 to find out estimate
    number of blogs.

    You can pass `progress_fn` function to track progress of the binary search.

    Args:
        progress_fn (fn): Function accepting one parameter (current estimate).

    Returns:
        int: Number of published blogposts.
    """
    def test_end_of_bloglist(pagination):
        url = _shared.url_context("/blog/?from=%d" % (pagination * 25))
        data = _shared.download(url)
        dom = _dhtmlparser.parseString(_remove_crap_from_bloglist(data))

        if progress_fn:
            progress_fn(pagination)

        return _should_continue(dom)

    # 807 as of 20.02.2018
    estimated_max_no_blogs = (time.localtime().tm_year - 2000) * 50 + 100

    return _binary_search(0, estimated_max_no_blogs, test_end_of_bloglist)
