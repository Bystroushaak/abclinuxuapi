Changelog
=========

0.3.6
-----
    - Fixed problems with old blogs (different HTML).
    - Implemented #6: ``.__repr__()`` for all important classes.

0.3.5
-----
    - Added ``Comment.censored``.
    - ``Comment.registered_user`` renamed to ``Comment.registered``.
    - Fixed bug which skipped censored comments.

0.3.4
-----
    - Fixed parsing of censored comments.

0.3.3
-----
    - Added date_izolator(). Fixed bugs in comments parsing with relative dates.
    - Fixed bug in parsing of Blogpost's content.
    - Added blog iterator tor User object.
    - Fixed #4 - bug in username parsing.

0.3.2
-----
    - Implemented ``Blogpost.get_image_urls()``.

0.3.1
-----
    - Fixed bugs in user.py.
    - Added ``iter_blogposts()``, ``first_blog_page()`` functions for browsing the bloglist.

0.3.0
-----
    - Added parsing of comments under blogposts.
    - Fixed bugs.

0.2.0
-----
    - Added a lot of features.
    - Fixed broken setup.py.

0.1.0
-----
    - Created.
    - It can be now used to read data from the abclinuxu, but it is incomplete and it will need a lot of work to do.