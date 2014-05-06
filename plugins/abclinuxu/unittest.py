#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from __init__ import *


#= Variables ==================================================================
#= Functions & objects ========================================================
#= Main program ===============================================================
if __name__ == '__main__':
    posts = User("bystroushaak").get_blogposts()
    assert len(posts) >= 56
    assert posts[0].title == "Google vyhledávání"
    assert posts[55].title == "Dogecoin"

    u = User("bystroushaak", open("pass").read().strip())
    # u.add_blogpost("test", "just test text")
    u.list_concepts()
