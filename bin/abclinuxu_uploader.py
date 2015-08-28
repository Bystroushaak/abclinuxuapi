#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import sys
import os.path
import getpass
import argparse

import dhtmlparser as d

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "../src")
)
import abclinuxuapi


# Variables ===================================================================
ALLOWED_IMAGES = [
    "jpg",
    "jpeg",
    "gif",
    "png"
]


# Functions & objects =========================================================
def get_body(dom):
    body = dom.find("body")
    if body:
        return body[0].getContent()

    return str(dom)


def upload_image(concept, image_path):
    # remote images
    if not os.path.exists(image_path):
        return image_path

    concept.add_pic(open(image_path))

    return concept.list_pics()[-1]


def upload_html(dom, args):
    user = abclinuxuapi.User(args.username, args.password)

    try:
        user.add_concept(get_body(dom), args.title)
    except ValueError, e:
        sys.stderr.write("Fail: " + e.message + "\n")
        sys.exit(1)

    concept = user.get_concepts()[-1]

    print "Uploading your concept '%s'" % concept.title
    print
    print "Uploading inlined images:"

    # upload inlined images
    for img in dom.find("img"):
        if "src" not in img.params:
            continue

        print "\tUploading '%s'" % os.path.basename(img.params["src"])

        img.params["src"] = upload_image(concept, img.params["src"])

    print
    print "Uploading linked images:"

    # upload linked images
    for a in dom.find("a"):
        if "href" not in a.params or "." not in a.params["href"]:
            continue

        if a.params["href"].rsplit(".", 1)[1].lower() not in ALLOWED_IMAGES:
            continue

        print "\tUploading '%s'" % os.path.basename(a.params["href"])

        a.params["href"] = upload_image(concept, a.params["href"])

    print
    print "Updating image links in concept .."

    try:
        concept.edit(get_body(dom))
    except ValueError, e:
        sys.stderr.write("Fail: " + e.message + "\n")
        sys.exit(1)

    print
    print "Done: " + concept.link


# Main program ================================================================
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

        if not title or not title[0].getContent().strip():
            sys.stderr.write("Can't find <title> in your document.")
            sys.stderr.write("Use --title switch.\n")
            sys.exit(1)

        args.title = title[0].getContent().strip()

    if args.password is None:
        args.password = getpass.getpass("Password for '%s': " % args.username)

    os.chdir(
        os.path.dirname(
            os.path.abspath(args.FN)
        )
    )
    upload_html(dom, args)
