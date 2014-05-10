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


def test_get_blogposts():
    posts = User("bystroushaak").get_blogposts()

    assert len(posts) >= 56
    assert posts[0].title == "Google vyhledávání"
    assert posts[55].title == "Dogecoin"


def test_add_concept():
    u = User("unittest", open("pass").read().strip())

    old_concept_list = u.get_concepts()

    u.add_concept("Text of the new concept", "Title of the concept")

    new_concept_list = u.get_concepts()

    assert len(old_concept_list) < len(new_concept_list)

    assert new_concept_list[-1].title == "Title of the concept"
    content = new_concept_list[-1].get_content()

    assert len(content) > 0

    print content

    # assert  == "Text of the new concept"
