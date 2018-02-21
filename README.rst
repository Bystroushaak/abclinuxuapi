Introduction
============

.. image:: https://badge.fury.io/py/abclinuxuapi.png
    :target: https://pypi.python.org/pypi/abclinuxuapi
    
.. image:: https://img.shields.io/pypi/pyversions/abclinuxuapi.svg
    :target: https://pypi.python.org/pypi/abclinuxuapi

.. image:: https://img.shields.io/pypi/l/abclinuxuapi.svg
    :target: https://github.com/Bystroushaak/abclinuxuapi/blob/master/LICENSE.txt

.. image:: https://readthedocs.org/projects/abclinuxuapi/badge/?version=latest
    :target: http://abclinuxuapi.readthedocs.org/

.. image:: https://img.shields.io/github/issues/Bystroushaak/abclinuxuapi.svg
    :target: https://github.com/Bystroushaak/abclinuxuapi/issues

This module contains basic API for crawling the http://abclinuxu.cz website.

Installation
------------
Module is hosted at `PYPI <https://pypi.python.org/pypi/abclinuxuapi/>`_, and
can be installed using `PIP <http://en.wikipedia.org/wiki/Pip_%28package_manager%29>`_:

::

    pip install abclinuxuapi

Documentation
-------------
Full module documentation is hosted at ReadTheDocs:
http://abclinuxuapi.readthedocs.org

Disclaimer
----------
The API was made by me (Bystroushaak) and it is not officially related to the
http://abclinuxu.cz project.

Examples
--------

Iterate over all published blogs:

.. code-block:: python

    >>> import abclinuxuapi
    >>> for blog in abclinuxuapi.iter_blogposts():
    ...  print blog.title
    ... 

::

    Czech blacklist 1.0.21
    iOS aplikace, filemanager, prehravani multimedii...
    ENCFS - lze doporucit? mozna uskali?
    Vývoj v C# + Oracle ODP.NET + EntityFramework
    Skončila svoboda?
    Abclinuxu - vyjádření k útokům
    Eliptické křivky - vztah Weierstrass, Montgomery, Edwards
    kopirovanie raspbianu na microsd kartu
    Půjdem dolem, půjdem horem?
    Podotčeno…
    Abclinuxu presmerovano...
    Dead man
    Valentýn 2018 (genderově korektní mikrozápisek)
    Textilosaurus - co je nového?
    Kvíz: Znáte český kraj?
    Název filmu
    Trilium Notes jako platforma pro mini-aplikace
    Marketingový "průzkum" pro zjištění obětí na další útok
    Vítězný únor 2018
    Reverse engineering komunikace Xorg a nvidia driveru
    Vtipná konstrukce v shellu
    Anketa: Kdy budou další presidentské volby v ČR?
    Debian 9 a data corruption s detektivní zápletkou
    Proč je tolik povyku s meltdownem mezi normálními usery
    Tabletové skúsenosti pre ľahší život.
    ...

Get structured information for specific blog:

.. code-block:: python

    >>> blog = abclinuxuapi.Blogpost("https://www.abclinuxu.cz/blog/bystroushaak/2017/9/autorske-okenko-neal-asher", lazy=False)
    >>> blog.created_ts
    1506733800.0
    >>> blog.last_modified_ts
    1508752260.0
    >>> blog.tags
    ['knihy', 'ProtectedByTagManager', 'recenze', 'sci-fi']
    >>> blog.has_tux
    False
    >>> blog.rating
    Rating(100%@5)
    >>> blog.readed
    1470
    >>> blog.comments_n
    73
    >>> blog.comments[65]
    Comment(username=andrea, id=18)
    >>> blog.comments[65].registered
    False
    >>> blog.comments[65].timestamp
    1506861120.0
    >>> print blog.comments[65].text
    supr blogísky, ráda je čtu.
    <p class="separator"></p>
    myslím že jsem tu od Tebe viděla souhrn knih, které jsi přečetl. měl bys třeba top50 sci-fi, které bych si určitě měla přečíst? nebo alespoň top 10, první trojka?
    >>> blog.comments[65].responses
    [Comment(username=bystroushaak, id=19)]
    >>> print blog.text
    <h2>Autorské okénko: Neal Asher</h2>


    <p>Dvacátého září jsem dočetl všechno...
