#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os.path

import pytest

import abclinuxu


# Fixtures ====================================================================
@pytest.fixture
def username_password():
    local_dir = os.path.dirname(__file__)
    pwd_file_path = os.path.join(local_dir, "login")

    if not os.path.exists(pwd_file_path):
        raise IOError(
            "Please create file `login` in tests/ directory.\n"
            "First line is username, second password for test user."
        )

    with open(pwd_file_path) as f:
        return f.read().splitlines()[:2]


@pytest.fixture
def username():
    return username_password()[0]


@pytest.fixture
def password():
    return username_password()[-1]


# Tests =======================================================================
def test_login(username, password):
    u = abclinuxu.User(username, password)
    u.login()

    with pytest.raises(UserWarning):
        u = abclinuxu.User(username, "bad password")
        u.login()


def test_get_blogposts():
    posts = abclinuxu.User("bystroushaak").get_blogposts()

    assert len(posts) >= 56
    assert posts[0].title == "Google vyhledávání"
    assert posts[55].title == "Dogecoin"


def test_add_concept(username, password):
    u = abclinuxu.User(username, password)

    old_concept_list = u.get_concepts()

    u.add_concept("Text of the new concept", "Title of the concept")

    new_concept_list = u.get_concepts()

    assert len(old_concept_list) < len(new_concept_list)

    assert new_concept_list[-1].title == "Title of the concept"
    content = new_concept_list[-1].get_content()

    assert len(content) > 0

    # print content

    # assert  == "Text of the new concept"