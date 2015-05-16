#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from setuptools import setup, find_packages
from docs import getVersion


# Variables ===================================================================
changelog = open('CHANGELOG.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


# Actual setup definition =====================================================
setup(
    name='abclinuxuapi',
    version=getVersion(changelog),
    description="API for http://abclinuxu.cz.",
    long_description=long_description,
    url='https://github.com/Bystroushaak/abclinuxuapi',

    author='Bystroushaak',
    author_email='bystrousak[a]kitakitsune.org',

    classifiers=[
        "Development Status :: 3 - Alpha",
        'Intended Audience :: Developers',

        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",

        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",

        "Natural Language :: Czech",
        "License :: OSI Approved :: MIT License",
    ],
    license='MIT',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    scripts=['bin/abclinuxu_uploader.py'],

    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "requests",
        "pyDHTMLParser"
    ],
    test_suite='py.test',
    tests_require=["pytest"],
    extras_require={
        "test": [
            "pytest"
        ],
        "docs": [
            "sphinx",
            "sphinxcontrib-napoleon",
        ]
    },
)
