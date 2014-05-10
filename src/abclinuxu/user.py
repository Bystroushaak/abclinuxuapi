#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import time
from string import Template

import requests
import dhtmlparser as d

from config import *
from concept import Concept
from blogpost import Blogpost, Rating


#= Variables ==================================================================
#= Functions & objects ========================================================
class User(object):
    def __init__(self, username, password=None):
        self.username = username
        self.password = password
        self.logged_in = False

        self.blog_url = Template(BLOG_URL).substitute(USERNAME=self.username)
        self.session = requests.Session()

    def _get(self, url, params=None, as_text=True):
        """
        Shortcut for ``self.session.get().text.encode("utf-8")``.

        Args:
            url (str): Url on which the GET request will be sent.
            params (dict): GET parameters.
            as_text (bool, default True): Return result as text or binary data.

        Returns:
            str/binary data: depending on the `as_text` parameter.
        """
        data = self.session.get(url, params=params)
        return data.text.encode("utf-8") if as_text else data.content

    def _parse_timestamp(self, meta):
        """
        Parse number timestamp from the date representation.

        Args:
            meta (str): Meta html from the blogpost body.

        Returns:
            int: Timestamp.
        """
        date = filter(
            lambda x: ":" in x and "." in x,
            str(meta).splitlines()
        )[0].strip()
        return time.mktime(time.strptime(date, "%d.%m.%Y %H:%M"))

    def _parse_comments_n(self, meta):
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

    def _parse_rating(self, meta):
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
        # None is returned automatically

    def _parse_intro(self, blog, meta, title_tag):
        """
        Parse intro from the `meta` HTML part.
        """
        intro = blog.getContent().replace(str(meta), "")
        intro = intro.replace(str(title_tag), "")

        signature = blog.find("div", {"class": "signature"})
        if signature:
            intro = intro.replace(str(signature[0]), "")

        return d.removeTags(intro.strip()).strip()

    def login(self, password=None):
        """
        Logs the user in, tests, if the user is really logged.

        Args:
            password (str, default None): Password, overwrites the password set
                     when the object was created.

        Raises:
            UserWarning: if there was some error during login.
        """
        if self.logged_in:
            return

        if password is not None:
            self.password = password

        if self.password is None:
            raise UserWarning("Invalid password.")

        data = self.session.post(
            LOGIN_URL,
            data={
                "finish": "Přihlásit",
                "LOGIN": self.username,
                "PASSWORD": self.password,
                "noCookie": "no",
                "useHttps": "yes" if LOGIN_URL.startswith("https") else "no",
                "action": "login2",
                "url": "http://www.abclinuxu.cz/"
            }
        ).text.encode("utf-8")

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

        self.logged_in = True

    def get_blogposts(self):
        """
        Lists all of users PUBLISHED blogposts.

        Warning:
            Concepts are NOT icluded.

        Return: sorted (old->new) list of Blogpost objects.
        """
        posts = []

        cnt = 0
        parsed = [1]  # just placeholder for first while iteration
        while parsed:
            parsed = []

            # download data from BASE_URL template
            data = self._get(
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
            cnt += STEP

        return sorted(posts, key=lambda x: x.timestamp)

    def get_concepts(self):
        """
        Returns:
            list: of Concept objects.

        Note:
            Concepts are unpublished Blogpost and has almost same properties.
        """
        self.login()

        # get the fucking untagged part of the site, where the links to the
        # concepts are stored
        data = self._get(self.blog_url)

        if '<div class="s_nadpis">Rozepsané zápisy</div>' not in data:
            return []

        data = data.split('<div class="s_nadpis">Rozepsané zápisy</div>')[1]

        dom = d.parseString(data)
        concept_list = dom.find("div", {"class": "s_sekce"})[0]

        # links to concepts are stored in <li>
        concepts = []
        for li in concept_list.find("li"):
            a = li.find("a")[0]

            concepts.append(
                Concept(a.getContent().strip(), a.params["href"], self.session)
            )

        return concepts

    def add_concept(self, text, title, timestamp_of_pub=None):
        """
        Adds new concept into your concepts.

        Args:
            text (str): Text of your concept.
            title (str): Title of your contept. Do not use HTML in title!
            timestamp_of_pub (int/float, default None): Timestamp of the
                publication date.

        Raises:
            UserWarning: if the site is broken or user was logged out.
        """
        self.login()

        dom = d.parseString(self._get(self.blog_url))

        # get section with links to new blog
        s_sekce = filter(
            lambda x: "Vlož nový zápis" in x.getContent(),
            dom.find("div", {"class": "s_sekce"})
        )
        if not s_sekce:
            raise UserWarning("Can't resolve right div tag!")

        # get link to "add blog" page
        add_blog_link = filter(
            lambda x: "href" in x.params and
                      x.params["href"].endswith("action=add"),
            s_sekce[0].find("a")
        )
        if not add_blog_link:
            raise UserWarning("Can't resolve user number!")
        add_blog_link = add_blog_link[0].params["href"]

        # get "add blog" page
        data = self._get(ABCLINUXU_URL + add_blog_link)
        dom = d.parseString(data)

        form_action = dom.find("form", {"name": "form"})[0].params["action"]

        data = self.session.post(
            ABCLINUXU_URL + form_action,
            data={
                "cid": 0,
                "publish": "",  # TODO: timestamp_of_pub
                "content": text,
                "title": d.removeTags(title),
                "delay": "Do konceptů",
                "action": "add2"
            }
        )
        data = data.text.encode("utf-8")
        check_error_div(data, '<div class="error" id="contentError">')
