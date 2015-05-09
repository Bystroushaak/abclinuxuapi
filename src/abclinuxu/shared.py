#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time


# Variables ===================================================================
ABCLINUXU_URL = "https://www.abclinuxu.cz"


# Functions & classes =========================================================
def first(inp_data):
    return next(x for x in inp_data)


def date_to_timestamp(date):
    date = date.strip()

    if len(date) <= 11:  # new blogs are without year
        date = date.replace(". ", ".%d " % time.localtime().tm_year)

    return time.mktime(time.strptime(date, "%d.%m.%Y %H:%M"))
