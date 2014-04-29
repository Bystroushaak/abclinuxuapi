#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from string import Template
from collections import namedtuple

import dhtmlparser as d
from httpkie import Downloader


#= Variables ==================================================================
ABCLINUXU_URL = "http://www.abclinuxu.cz"
BASE_URL = ABCLINUXU_URL + "/blog/$USERNAME/?from=$COUNTER"
STEP = 50


class Blogpost(namedtuple("Blogpost", ["title",
                                       "intro",
                                       "link",
                                       "comments_n"])):
    pass


class Rating(namedtuple("Rating", ["rating", "base"])):
    pass


#= Functions & objects ========================================================
def get_posts(username):
    posts = []

    cnt = 0
    parsed = [1]
    downer = Downloader()
    while parsed:
        parsed = []

        data = downer.download(
            Template(BASE_URL).substitute(
                USERNAME=username,
                COUNTER=cnt
            )
        )

        data = data.split(
            '<div class="s_nadpis linkbox_nadpis">Píšeme jinde</div>'
        )[0]
        data = data.split('<div class="st" id="st">')[1]

        dom = d.parseString(data)
        for blog in dom.find("div", {"class": "cl"}):
            # print blog

            # parse link and title
            title_tag = blog.find("h2", {"class": "st_nadpis"})[0]
            link = ABCLINUXU_URL + title_tag.find("a")[0].params["href"]
            title = d.removeTags(title_tag).strip()

            print "title:", title
            print "link:", link

            meta = blog.find("p", {"class": "meta-vypis"})[0]
            date = filter(
                lambda x: ":" in x and "." in x,
                str(meta).splitlines()
            )[0].strip()
            print "date:", date

            comments = meta.find("a")[-1].getContent()
            comments = comments.split("&nbsp;")[1]
            comments = int(comments)
            print "comments:", comments

            rating = filter(
                lambda x: "Hodnocení:" in x,
                str(meta).splitlines()
            )
            if rating:
                rating = rating[0].strip().replace("(", "")
                rating = rating.split("&nbsp;")
                rating = Rating(rating[1], rating[3])
            else:
                rating = None
            print "rating:", rating

            print meta

            # parse intro
            intro = blog.getContent().replace(str(meta), "")
            intro = intro.replace(str(title_tag), "")
            intro = intro.replace(
                str(blog.find("div", {"class": "signature"})[0]),
                ""
            )
            intro = d.removeTags(intro.strip()).strip()

            print intro
            print "----"

            # print intro[0].getContent()

        # print data
        break

        cnt += STEP




#= Main program ===============================================================
if __name__ == '__main__':
    get_posts("bystroushaak")
