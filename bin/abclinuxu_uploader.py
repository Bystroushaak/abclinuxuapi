#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import sys
import shutil
import os.path
import getpass
import argparse

import dhtmlparser as d

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
import abclinuxuapi


# Variables ===================================================================
ALLOWED_IMAGES = [
    "jpg",
    "jpeg",
    "gif",
    "png"
]
MB = 1024 * 1024


# Functions & objects =========================================================
def get_body(dom):
    body = dom.find("body")
    if body:
        return body[0].getContent()

    return str(dom)


def upload_image(concept, image_path, images_url=None):
    # remote images
    if not os.path.exists(image_path):
        return image_path

    if os.stat(image_path).st_size >= (MB - 1):
        return _use_remote_url_for_image(image_path, images_url)

    concept.add_pic(open(image_path))

    return concept.list_pics()[-1]


def _use_remote_url_for_image(image_path, images_url):
        if not images_url:
            msg = "Image `%s` is bigger than 1 MB. Please supply --url parameter to link them (see --help).\n"
            sys.stderr.write(msg % image_path)
            sys.exit(1)

        separator = "" if images_url.endswith("/") else "/"
        url = images_url + separator + os.path.basename(image_path)

        local_images_dir = "images_to_upload"
        try:
            os.makedirs(local_images_dir)
        except Exception:
            pass

        shutil.copy(image_path, local_images_dir)
        return url


def upload_html(dom, args, images_url=None):
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

        img.params["src"] = upload_image(concept, img.params["src"], images_url)

    print
    print "Uploading linked images:"

    # upload linked images
    for a in dom.find("a"):
        if "href" not in a.params or "." not in a.params["href"]:
            continue

        if a.params["href"].rsplit(".", 1)[1].lower() not in ALLOWED_IMAGES:
            continue

        print "\tUploading '%s'" % os.path.basename(a.params["href"])

        a.params["href"] = upload_image(concept, a.params["href"], images_url)

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
        "--username",
        metavar="USER",
        required=True,
        type=str,
        help="Your username."
    )
    parser.add_argument(
        "-p",
        "--password",
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
        help="Title of your blogpost. If not set, <title> tag from your \
              document is used."
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="URL where you'll put big images. At this moment, abclinuxu can't \
              upload images bigger than 1 MB. All such files will be put into \
              separate directory, which you can then upload to this URL and they \
              will point there."
    )
    args = parser.parse_args()

    if not os.path.exists(args.FN):
        sys.stderr.write("File '%s' doesn't exists!\n" % args.FN)
        sys.exit(1)

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
    upload_html(dom, args, images_url=args.url)
