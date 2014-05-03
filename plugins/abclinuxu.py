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
ABCLINUXU_URL = "https://www.abclinuxu.cz"
BLOG_URL = ABCLINUXU_URL + "/blog/$USERNAME"
BASE_URL = BLOG_URL + "/?from=$COUNTER"
LOGIN_URL = ABCLINUXU_URL + "/Profile"

_STEP = 50  # sets how much blogpost can be at one page


class Rating(namedtuple("Rating", ["rating", "base"])):
    pass


#= Functions & objects ========================================================
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


class User(object):
    def __init__(self, username, password=None):
        self.username = username
        self.password = password

        self.downer = Downloader()

    def _parse_timestamp(self, meta):
        date = filter(
            lambda x: ":" in x and "." in x,
            str(meta).splitlines()
        )[0].strip()
        return time.mktime(time.strptime(date, "%d.%m.%Y %H:%M"))

    def _parse_comments_n(self, meta):
        comments = meta.find("a")[-1].getContent()
        comments = comments.split("&nbsp;")[1]
        return int(comments)

    def _parse_rating(self, meta):
        rating = filter(
            lambda x: "Hodnocení:" in x,
            str(meta).splitlines()
        )

        if rating:
            rating = rating[0].strip().replace("(", "")
            rating = rating.split("&nbsp;")
            return Rating(rating[1], rating[3])
        # None is returned automatically

    def _parse_intro(self, blog, meta, title_tag):
        intro = blog.getContent().replace(str(meta), "")
        intro = intro.replace(str(title_tag), "")

        signature = blog.find("div", {"class": "signature"})
        if signature:
            intro = intro.replace(str(signature[0]), "")

        return d.removeTags(intro.strip()).strip()

    def get_blogposts(self):
        """
        Return: sorted (old->new) list of Blogpost objects.
        """
        posts = []

        cnt = 0
        parsed = [1]  # just placeholder for first while iteration
        while parsed:
            parsed = []

            # download data from BASE_URL template
            data = self.downer.download(
                Template(BASE_URL).substitute(
                    USERNAME=self.username,
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
                        comments_n=self._parse_comments_n(meta),
                        rel_link=rel_link,
                        link=link,
                        timestamp=self._parse_timestamp(meta),
                        rating=self._parse_rating(meta),
                        intro=self._parse_intro(blog, meta, title_tag)
                    )
                )

            posts.extend(parsed)
            cnt += _STEP

        return sorted(posts, key=lambda x: x.timestamp)

    def login(self):
        assert self.password is not None, "Invalid password."

        data = self.downer.download(
            LOGIN_URL,
            post={
                "finish": "Přihlásit",
                "LOGIN": self.username,
                "PASSWORD": self.password,
                "noCookie": "no",
                "useHttps": "yes" if LOGIN_URL.startswith("https") else "no",
                "action": "login2",
                "url": "http://www.abclinuxu.cz/"
            }
        )

        # test, whether the user is successfully logged in
        dom = d.parseString(data)

        logged_in = dom.find("div", {"class": "hl"})
        if not logged_in:
            raise UserWarning("Bad username/password!")

        logged_in = logged_in[0].find("div", {"class": "hl_vpravo"})
        if not logged_in:
            raise UserWarning("Bad username/password!")

        logged_in = logged_in[0].find("a")[-1]
        if not logged_in or logged_in.getContent() != "Odhlásit":
            raise UserWarning("Bad username/password!")

    def add_blogpost(self, title, text):
        self.login()

        data = self.downer.download(BLOG_URL)
        print data

#= Main program ===============================================================
if __name__ == '__main__':
    posts = User("bystroushaak").get_blogposts()
    assert len(posts) >= 56
    assert posts[0].title == "Google vyhledávání"
    assert posts[55].title == "Dogecoin"

    u = User("bystroushaak", "")
    u.add_blogpost("test", "just test text")
