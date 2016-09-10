#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from urlparse import urljoin

import requests
import dhtmlparser

import shared
from shared import first
from shared import url_context
from shared import ABCLINUXU_URL
from shared import check_error_div

from concept import Concept
from blogpost import Blogpost


# Variables ===================================================================
BLOG_STEP = 50  # Sets how much blogpost can be at one page


# Functions & classes =========================================================
class User(object):
    """
    Class that is used to hold informations about given `username`. You can
    also command various operations, like get list of all blogs, or add new
    concept.

    Attributes:
        username (str):
        password (str, default None): Password for logged user.
        logged_in (bool): Is the user logged in?
    """
    def __init__(self, username, password=None, lazy=False):
        """
        Args:
            username (str): Users login.
            password (str, default None): Optional password for given user.
                     This will allow you to upload concepts.
            lazy (bool, default False): Don't call :meth:`lazy_init` right when
                 the object is created.
        """
        self.username = username
        self.password = password
        self.logged_in = False

        self.session = requests.Session()
        self.blog_url = None
        self._user_id = None

        if not lazy:
            self.lazy_init()

    @property
    def has_blog(self):
        """
        Does the user have registered blog?
        """
        return self.blog_url is not None

    def lazy_init(self):
        """
        Parse additional informations about user. This step require one request
        to the site.
        """
        self.blog_url = self._parse_blogname()

    @staticmethod
    def from_user_id(user_id):
        """
        Transform `user_id` to instance of :class:`User`.

        Returns:
            obj: :class:`User` instance parsed from the `user_id`.
        """
        data = shared.download(url_context("/Profile/" + str(user_id)))
        dom = dhtmlparser.parseString(data)
        dhtmlparser.makeDoubleLinked(dom)

        shared.handle_errors(dom)

        # <li><a href="/lide/unittest/objekty" rel="nofollow">Seznam příspěvků
        # na abclinuxu.cz</a>
        a_tags = dom.find(
            "a",
            fn=lambda x: x.params.get("href", "").startswith("/lide/")
        )

        # pick only links which have content that starts with Seznam
        links = [
            a_tag.params["href"]
            for a_tag in a_tags
            if a_tag.getContent().startswith("Seznam")
        ]

        username = links[-1].split("/")[2]

        return User(username)

    def _get_user_id(self):
        """
        Resolve user's ID number for logged user.

        Returns:
            str: USER id as string.
        """
        if self._user_id is not None:
            return self._user_id

        self.login()
        dom = dhtmlparser.parseString(self._get(ABCLINUXU_URL))

        # resolve user's navigation panel
        nav_bar = dom.match(
            ["div", {"class": "hl_vpravo"}],
            {
                "tag_name": "a",
                "fn": lambda x: x.params.get("href", "").startswith("/Profile")
            }
        )

        if not nav_bar:
            raise ValueError("Can't parse user's navigation bar!")

        profile_link = first(nav_bar).params["href"]

        # transform /Profile/24642?action=myPage -> 24642
        self._user_id = profile_link.split("?")[0].split("/")[-1]

        return self._user_id

    def _compose_profile_url(self):
        return urljoin(ABCLINUXU_URL, urljoin("/lide/", self.username))

    def _parse_blogname(self):
        data = self._get(self._compose_profile_url())

        dom = dhtmlparser.parseString(data)
        blogname = filter(
            lambda x: x.getContent().strip().startswith("Můj blog: "),
            dom.find("h2")
        )

        if not blogname:
            return None

        links = blogname[0].find("a")

        if not links:
            raise UserWarning("Can't find blog link!")

        return urljoin(ABCLINUXU_URL, links[0].params["href"])

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
        return shared.download(
            url=url,
            params=params,
            session=self.session,
            as_text=as_text
        )

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

        login_url = urljoin(ABCLINUXU_URL, "/Profile")
        data = self.session.post(
            login_url,
            data={
                "finish": "Přihlásit",
                "LOGIN": self.username,
                "PASSWORD": self.password,
                "noCookie": "no",
                "useHttps": "yes" if login_url.startswith("https") else "no",
                "action": "login2",
                "url": "http://www.abclinuxu.cz/"
            },
            verify=False,
        ).text.encode("utf-8")

        # test, whether the user is successfully logged in
        dom = dhtmlparser.parseString(data)

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

    def _compose_blogposts_url(self, from_counter):
        return urljoin(self.blog_url, "?from=%d" % from_counter)

    def get_blogposts(self):
        """
        Lists all of users PUBLISHED blogposts. For unpublished, see 
        :meth:`get_concepts`.

        Returns:
            list: sorted (old->new) list of Blogpost objects.
        """
        if not self.has_blog:
            return []

        def cut_crap(data):
            data = data.split(
                '<div class="s_nadpis linkbox_nadpis">Píšeme jinde</div>'
            )[0]

            return data.split('<div class="st" id="st">')[1]

        cnt = 0
        posts = []
        parsed = [1]  # just placeholder for first iteration
        while parsed:
            data = self._get(self._compose_blogposts_url(cnt))

            dom = dhtmlparser.parseString(cut_crap(data))
            parsed = [
                Blogpost.from_html(blog_html)
                for blog_html in dom.find("div", {"class": "cl"})
            ]

            posts.extend(parsed)
            cnt += BLOG_STEP

        return sorted(posts, key=lambda x: x.created_ts)

    def get_concepts(self):
        """
        Return all concepts (unpublished blogs).

        Returns:
            list: List of Concept objects.
        """
        if not self.has_blog:
            raise ValueError("User doesn't have blog!")

        self.login()

        # get the fucking untagged part of the site, where the links to the
        # concepts are stored
        data = self._get(self.blog_url)

        if '<div class="s_nadpis">Rozepsané zápisy</div>' not in data:
            return []

        data = data.split('<div class="s_nadpis">Rozepsané zápisy</div>')[1]

        dom = dhtmlparser.parseString(data)
        concept_list = dom.find("div", {"class": "s_sekce"})[0]

        # links to concepts are stored in <li>
        concepts = []
        for li in concept_list.find("li"):
            a = li.find("a")[0]

            concepts.append(
                Concept(
                    title=a.getContent().strip(),
                    link=a.params["href"],
                    session=self.session
                )
            )

        return concepts

    def add_concept(self, text, title, ts_of_pub=None):
        """
        Adds new concept into your concepts.

        Args:
            text (str): Text of your concept.
            title (str): Title of your contept. Do not use HTML in title!
            ts_of_pub (int/float, default None): Timestamp of the publication.

        Raises:
            UserWarning: if the site is broken or user was logged out.
        """
        if not self.has_blog:
            raise ValueError("User doesn't have blog!")

        self.login()

        dom = dhtmlparser.parseString(self._get(self.blog_url))

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
        dom = dhtmlparser.parseString(data)

        form_action = dom.find("form", {"name": "form"})[0].params["action"]

        data = self.session.post(
            ABCLINUXU_URL + form_action,
            data={
                "cid": 0,
                "publish": shared.ts_to_concept_date(ts_of_pub),
                "content": text,
                "title": dhtmlparser.removeTags(title),
                "delay": "Do konceptů",
                "action": "add2"
            },
            verify=False,
        )
        data = data.text.encode("utf-8")
        check_error_div(data, '<div class="error" id="contentError">')

    def register_blog(self, blog_name):
        """
        Register blog under `blog_name`. Users doesn't have blogs
        automatically, you have to create them manually.

        Raises:
            UserWarning: If user already have blog registered.
            ValueError: If it is not possible to register blog for user (see \
                        exception message for details).
        """
        if self.has_blog:
            raise UserWarning("User already have blog!")

        add_blog_url = urljoin(
            ABCLINUXU_URL,
            urljoin("/blog/edit/", self._get_user_id())
        )

        data = self.session.post(
            add_blog_url,
            params={
                "blogName": blog_name,
                "category1": "",
                "category2": "",
                "category3": "",
                "action": "addBlog2",
            },
            verify=False,
        )

        # check for errors
        dom = dhtmlparser.parseString(data.text.encode("utf-8"))
        errors = dom.find("p", {"class": "error"})
        if errors:
            raise ValueError(first(errors).getContent())

        self.blog_url = self._parse_blogname()

        if not self.has_blog:
            raise ValueError("Couldn't register new blog.")

    def __iter__(self):
        for blog in self.get_blogposts():
            yield blog

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.username)
