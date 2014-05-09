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

STEP = 50  # sets how much blogpost can be at one page


def check_error_div(data, error_div):
    # no sophisticated parsing of the error is needed
    if error_div in data:
        data = data.split(error_div)[1]
        data = data.split("</div>")[0]

        raise ValueError(data)
