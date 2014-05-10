#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This submodule uses pytest framework: http://pytest.org

To run the tests:

    pip install pytest
    py.test abclinuxu/unittest.py
"""
#= Imports ====================================================================
import pytest

from __init__ import *


#= Variables ==================================================================
#= Functions & objects ========================================================
def test_login():
    u = User("unittest", open("pass").read().strip())
    u.login()

    with pytest.raises(UserWarning):
        u = User("unittest", "bad password")
        u.login()


def test_blogpost_fetching():
    u = User("bystroushaak")
    posts = u.get_blogposts()

    assert len(posts) >= 56
    assert posts[0].title == "Google vahledávání"
    assert posts[55].title == "Dogecoin"


#= Main program ===============================================================
if __name__ == '__main__':
    pass
    # u.add_concept("test2", 'just some text <p class="separator"></a>')
    # print u.get_concepts()[0].get_full_text()
    # print u.get_concepts()[0].edit("new text")
    # print u.get_concepts()[0].add_picture(open("/home/bystrousak/funyarinpa_drak.jpg"))
