# -*- encoding: utf-8 -*-
"""
Collection of non-typespecific tests.
"""

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import requests
from six.moves.urllib import parse


def check_accecpt_encoding(url):
    """
    Pass an URL and check wether mandatory compressions are supported.

    Section 4.11
    Args:
        url: URL to some json

    Returns:
        True on success, false otherwise.
    """
    compressions = ["gzip", "compress", "deflate"]
    header = {"Accept-Encoding": ", ".join(compressions)}
    response = requests.get(url, headers=header)

    # response shall contain header w/ "Content-Encoding" wich must be
    # any of the above
    if "content-encoding" not in response.headers:
        return False

    for compression in compressions:
        if compression in response.headers["content-encoding"]:
            return True
    return False


def check_not_contain_reserved_url_params(url):
    """
    Pass an URL and check if it does not contains reserved keywords.

    Section 4.13
    Args:
        url: some URL
    Returns:
        True if no reserved keys found, false otherwise.
    """
    reserved_keys = [
        "startdate",
        "enddate",
        "listformat",
        "subject",
        "predicate",
        "object"
    ]
    parsed_url = parse.urlparse(url)
    query = parse.parse_qs(parsed_url.query)
    for key in reserved_keys:
        if key in query:
            return False
    return True
