Changelog
=========

0.4.11
------
    - Added banlist for comment parsing on certain blogs (see HTML source on http://abclinuxu.cz/blog/Strider_BSD_koutek/2006/8/objevil-jsem-ameriku for details).

0.4.0 - 0.4.10
--------------
    - Added badges to README.
    - ``Blogpost.comments`` are now by default blank list instead of None.
    - Fixed bugs in uploader.
    - Parsing of the tags updated.
    - Added support for Blog.uid.
    - Fixed bugs in tests (new year parsing).
    - Added possibility to bypass lazy tag parsing.
    - Fixed bug in date parsing function.
    - Added support for parsing of more obscure date formats used by articles on abclinuxu.
    - Fixed another bug in date parsing function.
    - Added `verify=False`, because the SSL library pisses me off.
    - Added another special case of parsing the date.
    - Fixed another problem with date formats.
    - Fixed problem with parsing comments on the http://abclinuxu.cz/blog/msk/2016/8/hlada-sa-linux-embedded-vyvojar - there are no links to comments.
    - Fixed comment parsing in case of http://abclinuxu.cz/blog/leos/2007/2/prepis-diskusniho-fora-hw-sekce#31

0.3.0 - 0.3.11
-------------
    - Added parsing of comments under blogposts.
    - Fixed bugs.
    - Fixed bugs in user.py.
    - Added ``iter_blogposts()``, ``first_blog_page()`` functions for browsing the bloglist.
    - Implemented ``Blogpost.get_image_urls()``.
    - Added date_izolator(). Fixed bugs in comments parsing with relative dates.
    - Fixed bug in parsing of Blogpost's content.
    - Added blog iterator tor User object.
    - Fixed #4 - bug in username parsing.
    - Fixed parsing of censored comments.
    - Added ``Comment.censored``.
    - ``Comment.registered_user`` renamed to ``Comment.registered``.
    - Fixed bug which skipped censored comments.
    - Fixed problems with old blogs (different HTML).
    - Implemented #6: ``.__repr__()`` for all important classes.
    - Fixed #7 - blogs with opening HTML comments in perex.
    - Fixed bug in ``Blogpost._parse_content_tag()``.
    - Another attempt to solve shit in old blogs. There are missing tags, crossed tags and a lot of other shitfucks.
    - Fixed bug caused by http://abclinuxu.cz/blog/Mostly_IMDB/2008/6/radeon-hd-4850-a-tak-vubec#17
    - Added a lot of documentation, fixed docstrings and so on.
    - ``User.has_blog()`` changed to `bool` property ``User.has_blog``.
    - ``Concept`` class refactored.
    - Added new parameter ``data`` for ``shared.download()``.
    - ``User.ts_to_concept_date`` moved to ``shared.ts_to_concept_date()``.

0.2.0
-----
    - Added a lot of features.
    - Fixed broken setup.py.

0.1.0
-----
    - Created.
    - It can be now used to read data from the abclinuxu, but it is incomplete and it will need a lot of work to do.