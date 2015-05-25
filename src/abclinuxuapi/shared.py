#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import types
import datetime
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

    today = time.strftime("%d.%m.%Y", time.localtime())
    yesterday = datetime.date.today() - datetime.timedelta(days=-1)

    date = date.replace("dnes", today)
    date = date.replace("včera", yesterday.strftime("%d.%m.%Y"))

    if len(date) <= 11:  # new items are without year
        date = date.replace(". ", ".%d " % time.localtime().tm_year)

    return time.mktime(time.strptime(date, "%d.%m.%Y %H:%M"))


def date_izolator(lines):
    """
    Return all lines, that looks like it may be date in one of three
    abclinuxu formats.

    Args:
        lines (list): List of strings with lines which ma by dates.

    Returns:
        list: List of lines, which looks like they may contain dates.
    """
    return [
        x for x in lines
        if ":" in x and any(["." in x, "včera" in x, "dnes" in x])
    ]


def parse_timestamp(meta):
    """
    Parse numeric timestamp from the date representation.

    Args:
        meta (str): Meta html from the blogpost body.

    Returns:
        int: Timestamp.
    """
    if type(meta) not in [list, tuple, types.GeneratorType]:
        meta = str(meta).splitlines()

    date = date_izolator(meta)
    assert date, "Date not found!"

    return date_to_timestamp(first(date))


def url_context(url):
    return urljoin(ABCLINUXU_URL, url)


def handle_errors(dom):
    error = dom.find(
        "h1",
        {"class": "st_nadpis"},
        fn=lambda x: x.getContent() == "Chyba"
    )

    if error:
        error = first(error)

        # I want <p> next to <h1> with error
        elements = error.parent.childs
        elements = elements[elements.index(error):]

        error_msg = first(x for x in elements if x.getTagName() == "p")

        raise UserWarning(error_msg.getContent())
