#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import re
import time
import types
import datetime
from urlparse import urljoin

import requests
import dhtmlparser


# Variables ===================================================================
ABCLINUXU_URL = "https://www.abclinuxu.cz"  #: Base URL of the abclinuxu.
SESSION = requests.Session()  #: Session which is used in non-private requests.


# Functions & classes =========================================================
def download(url, params=None, method="GET", session=None, as_text=True,
             data=None):
    """
    Download data from `url` using `method`. Send `params` if defined.

    Args:
        url (str): Absolute URL from which the data will be downloaded.
        params (dict, default None): Send parameters (GET/POST).
        data (dict, default None): Data which will be sent as body of the
             request.
        method (str, default "GET"): Use this method to send the request.
        session (obj, default None): If ``None``, shared :attr:`SESSION` object
                is used.
        as_text (bool, default True): Return content as ``UTF-8`` encoded
                string. If false ``bytes`` are returned.

    Returns:
        str/bytes: Content depending on the `as_text` attribute.
    """
    if session is None:
        session = SESSION

    content = session.request(
        method,
        url,
        params=params,
        data=data,
        verify=False,
    )

    return content.text.encode("utf-8") if as_text else content.content


def first(inp_data):
    """
    Return first element from `inp_data`, or raise StopIteration.

    Note:
        This function was created because it works for generators, lists,
        iterators, tuples and so on same way, which indexing doesn't.

        Also it have smaller cost than list(generator)[0], because it doesn't
        convert whole `inp_data` to list.

    Args:
        inp_data (iterable): Any iterable object.

    Raises:
        StopIteration: When the `inp_data` is blank.
    """
    return next(x for x in inp_data)


def date_to_timestamp(date):
    """
    Convert abclinuxu `relative` or `absolute` date string in czech words to
    timestamp.

    Args:
        date (str): One of many abclinuxu representations of date string.

    Returns:
        int: Timestamp.
    """
    date = date.strip()
    date = date.__str__().replace(". ", ".")  # 10. 10. 2003 -> 10.10.2003

    # references to today and yesterday
    today = time.strftime("%d.%m.%Y", time.localtime())
    yesterday = datetime.date.today() - datetime.timedelta(days=-1)

    # 8.4.23:30
    if re.match(r"[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}\:[0-9]{1,2}", date):
        date = "%d.%s" % (time.localtime().tm_year, date)
        return time.mktime(time.strptime(date, "%Y.%d.%m.%H:%M"))

    date = date.replace("dnes", today)
    date = date.replace("včera", yesterday.strftime("%d.%m.%Y"))
    if "|" in date:  # "%H:%M |" -> "%d.%m.%Y %H:%M"
        date = today + " " + date.replace(" |", "")

    if len(date) <= 11:  # new items are without year
        date = date.replace(". ", ".%d " % time.localtime().tm_year)

    return time.mktime(time.strptime(date, "%d.%m.%Y %H:%M"))


def date_izolator(lines):
    """
    Return all lines, that looks like it may be date in one of many
    abclinuxu formats.

    Args:
        lines (list): List of strings with lines which ma by dates.

    Returns:
        list: List of lines, which looks like they may contain dates.
    """
    return [
        x for x in lines
        if ":" in x and any(["." in x, "včera" in x, "dnes" in x, "|" in x])
    ]


def alt_izolator(lines):
    """
    Return all lines, that looks like it may be date "~~%d.%m. ~~" format.

    Args:
        lines (list): List of strings with lines which ma by dates.

    Returns:
        list: List of lines, which looks like they may contain dates.
    """
    return [
        l for l in lines
        if "." in l and re.match(r".*[0-9]{1,2}\.[0-9]{1,2}\..*", l)
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
        meta = meta.__str__().replace(". ", ".")  # 10. 10. 2003 -> 10.10.2003
        meta = str(meta).splitlines()

    date = date_izolator(meta)
    if date:
        return date_to_timestamp(first(date))

    # this is used in articles (article != blogpost)
    date = alt_izolator(meta)
    if date:
        date = first(date).split()[0].replace("|", "")
        return date_to_timestamp(date + " 00:00")

    assert date, "Date not found!"


def ts_to_concept_date(timestamp):
    """
    Convert numeric `timestamp` into format used by abclinuxu for concepts.

    Args:
        timestamp (int): Timestamp as float/int.

    Returns:
        str: Converted `timestamp`.
    """
    if not timestamp:
        return None

    # required format: 2005-01-25 07:12
    return time.strftime(
        "%Y-%m-%d %H:%M",
        time.localtime(timestamp)
    )


def url_context(rel_url):
    """
    Add `rel_url` to the absolute context with :attr:`ABCLINUXU_URL`.

    Args:
        rel_url (str): Relative URL.

    Returns:
        str: Absolute URL.
    """
    return urljoin(ABCLINUXU_URL, rel_url)


def handle_errors(dom):
    """
    Look for error divs in given `dom` tree.

    Args:
        dom (obj): :class:`dhtmlparser.HTMLElement` instance.

    Raises:
        UserWarning: With content of the error div if the div was found.
    """
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


def check_error_div(data, error_div):
    """
    Dunno about this, it was created long time ago and I have no idea.
    """
    # no sophisticated parsing of the error is needed
    if error_div in data:
        data = data.split(error_div)[1]
        data = data.split("</div>")[0]

        raise ValueError(data)


def check_error_page(data):
    """
    Handle other, special kind of errors.
    """
    dom = dhtmlparser.parseString(data)

    title = dom.find("title")

    if not title:
        return

    title = title[0].getContent()

    if title != "Chyba":
        return

    p = dom.find("p")

    error_text = p[0].getContent() if p else data

    raise ValueError(error_text.strip())
