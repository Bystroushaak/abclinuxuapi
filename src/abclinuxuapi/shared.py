#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
from urlparse import urljoin

import requests


# Variables ===================================================================
ABCLINUXU_URL = "https://www.abclinuxu.cz"
SESSION = requests.Session()


# Functions & classes =========================================================
def download(url, params=None, method="GET", session=None, as_text=True):
    if session is None:
        session = SESSION

    data = session.request(method, url, params=params)

    return data.text.encode("utf-8") if as_text else data.content


def first(inp_data):
    return next(x for x in inp_data)


def date_to_timestamp(date):
    date = date.strip()

    if len(date) <= 11:  # new blogs are without year
        date = date.replace(". ", ".%d " % time.localtime().tm_year)

    return time.mktime(time.strptime(date, "%d.%m.%Y %H:%M"))


def parse_timestamp(meta):
    """
    Parse numeric timestamp from the date representation.

    Args:
        meta (str): Meta html from the blogpost body.

    Returns:
        int: Timestamp.
    """
    date = filter(
        lambda x: ":" in x and "." in x,
        str(meta).splitlines()
    )

    assert date, "Date not found!"

    return date_to_timestamp(date[0])


def url_context(url):
    return urljoin(ABCLINUXU_URL, url)
