Changelog
=========

0.3.8
-----
    - Fixed bug in ``Blogpost._parse_content_tag()``.

0.3.7
-----
    - Fixed #7 - blogs with opening HTML comments in perex.

0.3.0 - 0.3.6
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

0.2.0
-----
    - Added a lot of features.
    - Fixed broken setup.py.

0.1.0
-----
    - Created.
    - It can be now used to read data from the abclinuxu, but it is incomplete and it will need a lot of work to do.