# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
"""
Collection of non-typespecific tests.
"""

import requests


class ServerTests():
    # TODO: doc me

    def check_accecpt_encoding(self, url):
        """
        Pass an url and check wether mandatory compressions are supported.

        Args:
            url: URL to some json

        Returns:
            True on success, false otherwise.
        """
        compressions = ["gzip", "compress", "deflate"]
        response = requests.get(
            url,
            {"Accept-Encoding": ", ".join(compressions)}
        )
        # response shall contain header w/ "Content-Encoding" wich must be
        # any of the above
        for compression in compressions:
            if compression in response.header["Content-Encoding"]:
                return True
        return False
