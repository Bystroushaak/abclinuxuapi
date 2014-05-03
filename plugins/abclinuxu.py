#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import time
from string import Template
from collections import namedtuple

import dhtmlparser as d
from httpkie import Downloader


#= Variables ==================================================================
ABCLINUXU_URL = "http://www.abclinuxu.cz"
BASE_URL = ABCLINUXU_URL + "/blog/$USERNAME/?from=$COUNTER"
STEP = 50


class Blogpost(namedtuple("Blogpost", ["title",
                                       "comments_n",
                                       "rel_link",
                                       "timestamp",
                                       "link",
                                       "rating",
                                       "intro"])):
    def get_full_text(self):
        raise NotImplementedError("Not implemented yet.")

    def get_comments(self):
        raise NotImplementedError("Not implemented yet.")


class Rating(namedtuple("Rating", ["rating", "base"])):
    pass


#= Functions & objects ========================================================
def _parse_timestamp(meta):
    date = filter(
        lambda x: ":" in x and "." in x,
        str(meta).splitlines()
    )[0].strip()
    return time.mktime(time.strptime(date, "%d.%m.%Y %H:%M"))


def _parse_comments_n(meta):
    comments = meta.find("a")[-1].getContent()
    comments = comments.split("&nbsp;")[1]
    return int(comments)


def _parse_rating(meta):
    rating = filter(
        lambda x: "Hodnocení:" in x,
        str(meta).splitlines()
    )

    if rating:
        rating = rating[0].strip().replace("(", "")
        rating = rating.split("&nbsp;")
        return Rating(rating[1], rating[3])
    # None is returned automatically


def _parse_intro(blog, meta, title_tag):
    intro = blog.getContent().replace(str(meta), "")
    intro = intro.replace(str(title_tag), "")

    signature = blog.find("div", {"class": "signature"})
    if signature:
        intro = intro.replace(str(signature[0]), "")

    return d.removeTags(intro.strip()).strip()


def get_posts(username):
    posts = []

    cnt = 0
    parsed = [1]  # just placeholder for while
    downer = Downloader()
    while parsed:
        parsed = []

        # download data from BASE_URL template
        data = downer.download(
            Template(BASE_URL).substitute(
                USERNAME=username,
                COUNTER=cnt
            )
        )

        # clean crap, get just content
        data = data.split(
            '<div class="s_nadpis linkbox_nadpis">Píšeme jinde</div>'
        )[0]
        data = data.split('<div class="st" id="st">')[1]

        dom = d.parseString(data)
        for blog in dom.find("div", {"class": "cl"}):
            # parse link and title
            title_tag = blog.find("h2", {"class": "st_nadpis"})[0]
            rel_link = title_tag.find("a")[0].params["href"]
            link = ABCLINUXU_URL + rel_link
            title = d.removeTags(title_tag).strip()

            # get meta
            meta = blog.find("p", {"class": "meta-vypis"})[0]

            parsed.append(
                Blogpost(
                    title=title,
                    comments_n=_parse_comments_n(meta),
                    rel_link=rel_link,
                    link=link,
                    timestamp=_parse_timestamp(meta),
                    rating=_parse_rating(meta),
                    intro=_parse_intro(blog, meta, title_tag)
                )
            )

        posts.extend(parsed)
        cnt += STEP

    return sorted(posts, key=lambda x: x.timestamp)


#= Main program ===============================================================
if __name__ == '__main__':
    posts = get_posts("bystroushaak")
    assert(len(posts) >= 56)
    assert(posts[0].title == "Google vyhledávání")
