#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os.path

import requests
import dhtmlparser as d

from config import *


#= Variables ==================================================================
#= Functions & objects ========================================================
class Concept:
    def __init__(self, title, rel_link, session):
        self.title = title
        self.rel_link = rel_link
        self.link = ABCLINUXU_URL + rel_link

        self.meta = None
        self.session = session

    def _init_metadata(self, data=None):
        if not data:
            data = self.session.get(self.link).text.encode("utf-8")

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

    def get_full_text(self):
        data = self.session.get(self.link).text.encode("utf-8")

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

    def edit(self, text, title=None):
        if not self.meta:
            self._init_metadata()

        data = self.session.get(ABCLINUXU_URL + self.meta["Uprav zápis"])
        data = data.text.encode("utf-8")
        # TODO: implement

    def remove(self):
        raise NotImplementedError("Not implemented yet.")

    def publish(self):
        raise NotImplementedError("Not implemented yet.")

    def add_picture(self, opened_file):
        """
        Add picture to the Concept.

        Args:
            opened_file (file): opened file object
        """
        # init meta
        if not self.meta:
            self._init_metadata()

        # get link to pic form
        data = self.session.get(
            ABCLINUXU_URL + self.meta["Přidej obrázek"]
        ).text.encode("utf-8")
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

    def list_pictures(self):
        raise NotImplementedError("Not implemented yet.")

    def __str__(self):
        return self.title
