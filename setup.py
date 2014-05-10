#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import shutil

from setuptools import setup, find_packages
from distutils.command.sdist import sdist

try:
    from docs import getVersion
except ImportError:  # during packaging, docs are moved to html_docs
    from html_docs import getVersion


changelog = open('CHANGELOG.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


class BuildSphinx(sdist):
    """
    Generates sphinx documentation, puts it into html_docs/, packs it to
    package and removes unused directory.
    """
    def run(self):
        d = os.path.abspath('.')
        DOCS = d + "/" + "docs"
        DOCS_IN = DOCS + "/build/html"
        DOCS_OUT = d + "/html_docs"

        if not self.dry_run:
            print "Generating the documentation .."

            os.chdir(DOCS)
            os.system("make clean")
            os.system("make html")

            if os.path.exists(DOCS_OUT):
                shutil.rmtree(DOCS_OUT)

            shutil.copytree(DOCS_IN, DOCS_OUT)
            shutil.copy(DOCS + "/__init__.py", DOCS_OUT)  # for getVersion()
            os.chdir(d)

        sdist.run(self)

        if os.path.exists(DOCS_OUT):
            shutil.rmtree(DOCS_OUT)


setup(
    name='abclinuxuapi',
    version=getVersion(changelog),
    description="API for http://abclinuxu.cz.",
    long_description=long_description,
    url='https://github.com/Bystroushaak/abclinuxu',

    author='Bystroushaak',
    author_email='bystrousak[a]kitakitsune.org',

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7",
        "Natural Language :: Czech",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)"
    ],
    license='GPLv2+',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    scripts=['bin/abclinuxu_uploader.py'],

    namespace_packages=['abclinuxu'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "requests",
        "pyDHTMLParser"
    ],

    # cmdclass={'sdist': BuildSphinx}
)
