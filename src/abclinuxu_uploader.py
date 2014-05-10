#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import sys
import os.path
import getpass
import argparse

import abclinuxu  # https://github.com/Bystroushaak/abclinuxuapi
import dhtmlparser as d


#= Variables ==================================================================
#= Functions & objects ========================================================
def upload_file(args):
    print args


#= Main program ===============================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="abclinuxu.cz blog uploader.")

    parser.add_argument(
        "FN",
        type=str,
        help="Filename of the HTML document, which will be parsed and uploaded."
    )
    parser.add_argument(
        "-u",
        '--username',
        metavar="USER",
        required=True,
        type=str,
        help="Your username."
    )
    parser.add_argument(
        "-p",
        '--password',
        metavar="PASS",
        type=str,
        default=None,
        help="Your password. If not set, you will be asked interactively."
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default=None,
        help="Title of your blogpost. If not set, <title> tag from your\
              document is used."
    )
    args = parser.parse_args()

    if not os.path.exists(args.FN):
        sys.stderr.write("File '%s' doesn't exists!\n" % args.FN)
        sys.exit(1)

    dom = None
    with open(args.FN) as f:
        data = f.read()
        dom = d.parseString(data)

    if args.title is None:
        title = dom.find("title")

        if not title:
            sys.stderr.write("Can't find <title> in your document.")
            sys.stderr.write("Use --title switch.\n")
            sys.exit(1)

        args.title = title[0].getContent().strip()

    if args.password is None:
        args.password = getpass.getpass("Password for '%s': " % args.username)

    upload_file(args)
