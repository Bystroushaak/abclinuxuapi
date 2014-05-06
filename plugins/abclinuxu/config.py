#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Variables ==================================================================
ABCLINUXU_URL = "https://www.abclinuxu.cz"
BLOG_URL = ABCLINUXU_URL + "/blog/$USERNAME"
BASE_URL = BLOG_URL + "/?from=$COUNTER"
LOGIN_URL = ABCLINUXU_URL + "/Profile"

_STEP = 50  # sets how much blogpost can be at one page
