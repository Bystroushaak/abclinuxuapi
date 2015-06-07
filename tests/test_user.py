#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os.path

import pytest

import abclinuxuapi


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


@pytest.fixture
def user():
    return abclinuxuapi.User(*username_password())


# Tests =======================================================================
def test_register_blog(user):
    if user.has_blog:
        return

    user.register_blog("Test user's blog")
    assert user.has_blog()


def test_login(user, username):
    user.login()

    with pytest.raises(UserWarning):
        user = abclinuxuapi.User(username, "bad password")
        user.login()


def test_get_blogposts():
    posts = abclinuxuapi.User("bystroushaak").get_blogposts()

    assert len(posts) >= 56
    assert posts[0].title == "Google vyhledávání"
    assert posts[55].title == "Dogecoin"


def test_add_concept(user):
    old_concept_list = user.get_concepts()

    user.add_concept("Text of the new concept", "Title of the concept")

    new_concept_list = user.get_concepts()

    assert len(old_concept_list) < len(new_concept_list)

    assert new_concept_list[-1].title == "Title of the concept"
    content = new_concept_list[-1].get_content()

    assert len(content) > 0

    assert "Text of the new concept" in content


def test_get_user_id(user):
    user.login()

    assert user._get_user_id()
    assert int(user._get_user_id())


def test_from_user_id():
    u = abclinuxuapi.User.from_user_id("19684")

    assert u.username == "bystroushaak"


def test_iterator():
    blogs = [blog for blog in abclinuxuapi.User("bystroushaak")]

    assert len(blogs) > 56
