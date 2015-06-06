abclinuxuapi
============

Python API for the http://abclinuxu.cz website.

API
---

Whole API is splitted into four submodules:

:doc:`/api/abclinuxuapi`:

.. toctree::
    :maxdepth: 1

    /api/user.rst
    /api/api.rst
    /api/blogpost.rst
    /api/comment.rst
    /api/concept.rst

And one file with shared functions:

.. toctree::
    :maxdepth: 1

    /api/shared.rst

Installation
------------
Module is hosted at `PYPI <https://pypi.python.org/pypi/abclinuxuapi>`_,
and can be easily installed using `PIP`_::

    sudo pip install abclinuxuapi

.. _PIP: http://en.wikipedia.org/wiki/Pip_%28package_manager%29

Source code
-----------
Project is released under MIT license. Source code can be found at GitHub:

- https://github.com/Bystroushaak/abclinuxuapi

Unittests
+++++++++

A lot of features of the project is tested by unittests. You can run those tests using provided ``run_tests.sh`` script, which can be found in the root of the project.

If you have any trouble, just add ``--pdb`` switch at the end of your ``run_tests.sh`` command like this: ``./run_tests.sh --pdb``. This will drop you to the `PDB`_ shell.

.. _PDB: https://docs.python.org/2/library/pdb.html

Requirements
^^^^^^^^^^^^
This script expects that package pytest_ is installed. In case you don't have it yet, it can be easily installed using following command::

    pip install --user pytest

or for all users::

    sudo pip install pytest

.. _pytest: http://pytest.org/

Note:
    Some of the tests also require file ``login`` placed in the ``tests/`` directory. If you don't provide this file, tests from ``test_user.py`` will fail.

    Example of the ``login`` file::

        username
        password

Example
^^^^^^^
::

    $ ./run_tests.sh 
    ============================= test session starts ==============================
    platform linux2 -- Python 2.7.6 -- py-1.4.27 -- pytest-2.7.0
    rootdir: /home/Dropbox/c0d3z/python/interface/abclinuxuapi, inifile: 
    collected 33 items 

    tests/test_blogpost.py ..........
    tests/test_comment.py ..........
    tests/test_init.py ...
    tests/test_shared.py ...
    tests/test_user.py .......

    ========================== 33 passed in 16.07 seconds ==========================

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
