#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import requests
import dhtmlparser as d

from config import *


#= Variables ==================================================================
#= Functions & objects ========================================================
class Concept:
    """
    This class represents concept of the blog - it has all attributes of the
    blog, but it is invisible for the readers.
    """
    def __init__(self, title, rel_link, session):
        self.title = title
        self.rel_link = rel_link
        self.link = ABCLINUXU_URL + rel_link

        self.meta = None
        self.session = session
        self.data = None

    def _get(self, url, params=None, as_text=True):
        data = self.session.get(url, params=params)
        return data.text.encode("utf-8") if as_text else data.content

    def _init_metadata(self, data=None):
        if not data:
            data = self._get(self.link)

        if '<div class="s_nadpis">Správa zápisku</div>' not in data:
            raise ValueError(
                "Can't parse metadata! It looks like I am not logged in!"
            )

        data = data.split('<div class="s_nadpis">Správa zápisku</div>')[1]

        dom = d.parseString(data)
        meta_list = dom.find("div", {"class": "s_sekce"})[0]

        self.meta = {}
        for li in meta_list.find("li"):
            a = li.find("a")[0]
            self.meta[a.getContent().strip()] = a.params["href"]

    def _refresh(self):
        self.data = self._get(self.link)

    def get_content(self):
        """
        Get content of this Concept.

        Returns:
            str: full HTML UTF-8 encoded text of the concept.
        """
        data = self._get(self.link)

        if not self.meta:
            self._init_metadata(data)

        # data = data.split('<div class="rating">')[0]
        data = data.rsplit('<!-- -->', 1)[0]

        # find beginning of the concept text
        dom = d.parseString(data)
        meta_vypis = dom.find("p", {"class": "meta-vypis"})
        if not meta_vypis:
            raise ValueError("Can't find meta-vypis <p>!")
        data = data.split(str(meta_vypis[0]))[1]

        return data.strip()

    def add_pic(self, opened_file):
        """
        Add picture to the Concept.

        Args:
            opened_file (file): opened file object
        """
        # init meta
        if not self.meta:
            self._init_metadata()

        # get link to pic form
        data = self._get(ABCLINUXU_URL + self.meta["Přidej obrázek"])
        dom = d.parseString(data)

        # get information from pic form
        form = dom.find("form", {"enctype": "multipart/form-data"})[0]
        add_pic_url = form.params["action"]

        # send pic
        data = self.session.post(
            ABCLINUXU_URL + add_pic_url,
            data={
                "action": "addScreenshot2",
                "finish": "Nahrát"
            },
            files={"screenshot": opened_file}
        )
        data = data.text.encode("utf-8")
        check_error_div(data, '<div class="error" id="screenshotError">')

    def list_pics(self):
        # init meta
        if not self.meta:
            self._init_metadata()

        data = self._get(ABCLINUXU_URL + self.meta["Správa příloh"])
        dom = d.parseString(data)

        form = dom.find("form", {"name": "form"})
        assert len(form) > 0, "Can't find pic form!"

        urls = []
        for a in form[0].find("a"):
            if "href" not in a.params:
                continue

            urls.append(a.params["href"])

        return urls

    def edit(self, text, title=None, timestamp_of_pub=None):
        if not self.meta:
            self._init_metadata()

        data = self._get(ABCLINUXU_URL + self.meta["Uprav zápis"])
        dom = d.parseString(data)

        form = dom.find("form", {"name": "form"})

        assert len(form) > 0, "Can't find edit form!"
        form = form[0]

        form_action = form.params["action"]

        if title is None:
            title = form.find("input", {"name": "title"})[0].params["value"]

        date = ""
        if timestamp_of_pub is None:
            date = form.find("input", {"name": "publish"})[0].params["value"]
        elif type(timestamp_of_pub) in [str, unicode]:
            date = timestamp_of_pub
        else:
            pass  # TODO: date processing

        data = self.session.post(
            ABCLINUXU_URL + form_action,
            data={
                "cid": 0,
                "publish": date,
                "content": text,
                "title": title,
                "delay": "Ulož",
                "action": "edit2"
            }
        )
        data = data.text.encode("utf-8")
        check_error_div(data, '<div class="error" id="contentError">')

    def __str__(self):
        return self.title

    def remove(self):
        raise NotImplementedError("Not implemented yet.")

    def publish(self):
        raise NotImplementedError("Not implemented yet.")
