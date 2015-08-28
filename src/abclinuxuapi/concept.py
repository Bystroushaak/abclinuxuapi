#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

from shared import first
from shared import download
from shared import url_context
from shared import check_error_div
from shared import check_error_page
from shared import ts_to_concept_date


# Class definition ============================================================
class Concept(object):
    """
    Attributes:
        title (str): Title of the concept.
        link (str): Absolute URL of the concept.
    """
    def __init__(self, title, link, session):
        self.title = title
        self.link = url_context(link)

        self._meta = None
        self._session = session

    def _init_metadata(self, data=None):
        if not data:
            data = download(self.link, session=self._session)

        if '<div class="s_nadpis">Správa zápisku</div>' not in data:
            raise ValueError(
                "Can't parse metadata! It looks like I am not logged in!"
            )

        data = data.split('<div class="s_nadpis">Správa zápisku</div>')[1]

        dom = dhtmlparser.parseString(data)
        meta_list = first(dom.find("div", {"class": "s_sekce"}))

        self._meta = {}
        for li in meta_list.find("li"):
            a = first(li.find("a"))
            self._meta[a.getContent().strip()] = a.params["href"]

    def get_content(self):
        """
        Get content of this Concept.

        Returns:
            str: full HTML UTF-8 encoded text of the concept.
        """
        data = download(self.link, session=self._session)

        if not self._meta:
            self._init_metadata(data)

        data = first(data.rsplit('<!-- -->', 1))

        # find beginning of the concept text
        dom = dhtmlparser.parseString(data)
        meta_vypis = dom.find("p", {"class": "meta-vypis"})
        if not meta_vypis:
            raise ValueError("Can't find meta-vypis <p>!")

        meta_vypis = first(meta_vypis)
        data = data.split(str(meta_vypis))[1]

        return data.strip()

    def add_pic(self, opened_file):
        """
        Add picture to the Concept.

        Args:
            opened_file (file): opened file object
        """
        # init meta
        if not self._meta:
            self._init_metadata()

        # get link to pic form
        data = download(
            url_context(self._meta["Přidej obrázek"]),
            session=self._session
        )
        dom = dhtmlparser.parseString(data)

        # get information from pic form
        form = first(dom.find("form", {"enctype": "multipart/form-data"}))
        add_pic_url = form.params["action"]

        # send pic
        data = self._session.post(
            url_context(add_pic_url),
            data={
                "action": "addScreenshot2",
                "finish": "Nahrát"
            },
            files={"screenshot": opened_file}
        )
        data = data.text.encode("utf-8")
        check_error_div(data, '<div class="error" id="screenshotError">')

    def list_pics(self):
        """
        Return:
            list: List of URLs to pictures used in this concept.
        """
        # init meta
        if not self._meta:
            self._init_metadata()

        data = download(
            url_context(self._meta["Správa příloh"]),
            session=self._session
        )
        dom = dhtmlparser.parseString(data)

        form = dom.find("form", {"name": "form"})
        assert form, "Can't find pic form!"

        return [
            a.params["href"]
            for a in first(form).find("a")
            if "href" in a.params
        ]

    def edit(self, text, title=None, date_of_pub=None):
        """
        Edit concept.

        Args:
            text (str): New text of the context.
            title (str, default None): New title of the concept. If not set,
                  old title is used.
            date_of_pub (str/int, default None): Date string in abclinuxu
                        format or timestamp determining when the concept should
                        be automatically published.

        Note:
            `date_of_pub` can be string in format ``"%Y-%m-%d %H:%M"``.
        """
        if not self._meta:
            self._init_metadata()

        data = download(
            url_context(self._meta["Uprav zápis"]),
            session=self._session
        )
        dom = dhtmlparser.parseString(data)

        form = dom.find("form", {"name": "form"})

        assert form, "Can't find edit form!"
        form = first(form)

        form_action = form.params["action"]

        if title is None:
            title = first(form.find("input", {"name": "title"}))
            title = title.params["value"]

        date = ""
        if date_of_pub is None:
            date = first(form.find("input", {"name": "publish"}))
            date = date.params["value"]
        elif isinstance(date_of_pub, basestring):
            date = date_of_pub
        else:
            date = ts_to_concept_date(date_of_pub)

        data = download(
            url=url_context(form_action),
            method="POST",
            data={
                "cid": 0,
                "publish": date,
                "content": text,
                "title": title,
                "delay": "Ulož",
                "action": "edit2"
            },
            session=self._session
        )
        check_error_div(data, '<div class="error" id="contentError">')
        check_error_page(data)

    def __str__(self):
        return self.title
