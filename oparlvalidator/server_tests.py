# -*- encoding: utf-8 -*-
"""
Collection of non-typespecific tests.
"""

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import requests


def check_accecpt_encoding(url):
    """
    Pass an url and check wether mandatory compressions are supported.

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
