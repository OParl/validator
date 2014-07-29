# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unittest
from .server import Server
from ..validator import ServerSuite


class TestCrawler(unittest.TestCase):
    # pylint: disable=protected-access

    def setUp(self):
        self.server = Server()

    def tearDown(self):
        self.server.shutdown()

    def test_validate_head_for_file_urls(self):
        self.server.serve({
            '/file_with_access_url': {
                'GET': {
                    'body': '{{"downloadUrl": "{}:{}/valid_download_url"}}'
                        .format(*self.server.httpd.server_address)}  # noqa
            },
            '/valid_download_url': {
                'HEAD': {'headers': [
                    ('Last-Modified', '23'),
                    ('Content-Disposition',
                        'attachment; filename="Wortprotokoll.pdf"')]}
            },
        })
        ServerSuite([('{}:{}/file_with_access_url',
                      'http://oparl.org/schema/1.0/File')]).validate()
