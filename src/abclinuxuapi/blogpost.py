#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
from collections import namedtuple

import dhtmlparser

from shared import first
from shared import ABCLINUXU_URL
from shared import date_to_timestamp


# Functions & objects =========================================================
class Rating(namedtuple("Rating", ["rating", "base"])):
    pass


class Blogpost(object):
    def __init__(self, url, lazy=True, **kwargs):
        self.url = url

        self.title = None
        self.intro = None
        self.text = None

        self.rating = None
        self.comments = None
        self.comments_n = 0

        self.created_ts = None
        self.last_modified_ts = None
        self.object_ts = time.time()

        # read parameters from kwargs
        for key, val in kwargs.iteritems():
            if key not in self.__dict__:
                raise TypeError("Unknown parameter `%s`!" % key)

            self.__dict__[key] = val

        if not lazy:
            self.pull()

    def pull():
        pass

    @staticmethod
    def _parse_intro(blog, meta, title_tag):
        """
        Parse intro from the `meta` HTML part.
        """
        intro = blog.getContent().replace(str(meta), "")
        intro = intro.replace(str(title_tag), "")

        signature = blog.find("div", {"class": "signature"})
        if signature:
            intro = intro.replace(str(signature[0]), "")

        return dhtmlparser.removeTags(intro.strip()).strip()

    @staticmethod
    def _parse_comments_n(meta):
        """
        Parse number of comments under the blogpost.

        Args:
            meta (str): Meta html from the blogpost body.

        Returns:
            int: Number of comments.
        """
        comments = meta.find("a")[-1].getContent()
        comments = comments.split("&nbsp;")[1]

        return int(comments)

    @staticmethod
    def _parse_rating(meta):
        """
        Parse rating of the blogpost.

        Args:
            meta (str): Meta html from the blogpost body.

        Returns:
            Rating: :class:`.Rating` object.
        """
        rating = filter(
            lambda x: "Hodnocení:" in x,
            str(meta).splitlines()
        )

        if rating:
            rating = rating[0].strip().replace("(", "")
            rating = rating.split("&nbsp;")

            return Rating(rating[1], rating[3])

    @staticmethod
    def _parse_timestamp(meta):
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

        return date_to_timestamp(date[0])

    @staticmethod
    def from_html(html):
        title_tag = first(html.find("h2", {"class": "st_nadpis"}))
        rel_link = first(title_tag.find("a")).params["href"]

        link = ABCLINUXU_URL + rel_link
        title = dhtmlparser.removeTags(title_tag).strip()

        # get meta
        meta = html.find("p", {"class": "meta-vypis"})[0]

        blog = Blogpost(url=link, lazy=True)

        blog.title = title
        blog.intro = Blogpost._parse_intro(html, meta, title_tag)
        blog.rating = Blogpost._parse_rating(meta)
        blog.created_ts = Blogpost._parse_timestamp(meta)
        blog.comments_n = Blogpost._parse_comments_n(meta)

        return blog

    def get_full_text(self):
        raise NotImplementedError("Not implemented yet.")

    def get_comments(self):
        raise NotImplementedError("Not implemented yet.")

    def edit(self):
        raise NotImplementedError("Not implemented yet.")

    def get_tags(self):
        raise NotImplementedError("Not implemented yet.")

    def get_number_of_reads(self):
        raise NotImplementedError("Not implemented yet.")
