# -*- encoding: utf-8 -*-
"""
Collection of non-type-specific tests.
"""

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import requests
# pylint: disable=import-error,no-name-in-module
from six.moves.urllib import parse
# pylint: enable=import-error,no-name-in-module


# TODO: Let’s not do this in the suite but on every request
# (without sending new requests).
def check_accept_encoding(url):
    """
    Pass an URL and check wether mandatory compressions are supported.

    Section 4.11
    Args:
        url: URL to some json

    Returns:
        True on success, false otherwise.
    """
    compressions = ['gzip', 'compress', 'deflate']
    header = {'Accept-Encoding': ', '.join(compressions)}
    response = requests.get(url, headers=header)

    # response shall contain header w/ 'Content-Encoding' wich must be
    # any of the above
    if 'content-encoding' not in response.headers:
        return False

    for compression in compressions:
        if compression in response.headers['content-encoding']:
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
        'startdate',
        'enddate',
        'listformat',
        'subject',
        'predicate',
        'object'
    ]
    parsed_url = parse.urlparse(url)
    query = parse.parse_qs(parsed_url.query)
    for key in reserved_keys:
        if key in query:
            return False
    return True


# TODO: Seems straightforward but if it is meant to test 4.12, then note that
# it’s not a requirement.
def check_http_status_codes(url_to_existing_get_ressource):
    """
    Pass an URL to some valid GET ressource and check if http status codes
    are good.
    """
    response = requests.get(url_to_existing_get_ressource)
    # 200
    if 'status' not in response.headers:
        return False
    if '200 OK' not in response.headers['status']:
        return False

    # 404
    bad_ressource = url_to_existing_get_ressource + \
        '/does/not/exist/unless/you/cheated'
    response = requests.get(bad_ressource)
    if 'status' not in response.headers:
        return False
    if '404 Not Found' not in response.headers['status']:
        return False

    # other codes testable?

    return True
