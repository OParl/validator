# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unittest
import json
from os.path import join, dirname
from os import walk
from ..crawler import Crawler
from .server import Server
from ..server_tests import (
    check_accept_encoding, check_not_contain_reserved_url_params,
    check_http_status_codes)

DATA_DIR = join(dirname(__file__), 'testdata')


class TestCrawler(unittest.TestCase):
    # pylint: disable=protected-access

    def setUp(self):
        self.server = Server()
        self.testdata = {}
        for root, _, files in walk(DATA_DIR):
            for filename in files:
                if filename.endswith(".valid.json"):
                    filepath = join(root, filename)
                    with open(filepath) as json_file:
                        data = json_file.read().decode('utf-8')
                        data = data.replace(
                            'https://oparl.example.org', self.server.url)
                        self.testdata[filename] = json.loads(data)

    def tearDown(self):
        self.server.shutdown()

    def test_accept_encoding(self):
        """
        Test for compression support (Section 4.11).
        """
        # setup server
        test_cases = {
            '/example/valid': {
                'GET':
                {
                    'headers': [('content-encoding', 'gzip')],
                }
            },
            '/example/invalid_empty': {
                'GET':
                {
                    'headers': [('content-encoding', '')],
                }
            },
            '/example/invalid_not_set': {
                'GET':
                {
                    'headers': [],
                }
            },
            '/example/invalid_type_not_supported': {
                'GET':
                {
                    'headers': [('content-encoding', 'esoteric')],
                }
            },
        }
        self.server.serve(test_cases)

        # run assertions
        prefix = 'http://localhost:%s' % self.server.port
        self.assertEquals(True,
                          check_accept_encoding(prefix + '/example/valid'))
        self.assertEquals(False,
                          check_accept_encoding(
                              prefix + '/example/invalid_empty'))
        self.assertEquals(False,
                          check_accept_encoding(
                              prefix + '/example/invalid_not_set'))
        self.assertEquals(False,
                          check_accept_encoding(
                              prefix + '/example/invalid_type_not_supported')
                          )

    def test_invalid_url_params(self):
        """
        Test for reserved key within queries (URLs) (Section 4.13).
        """
        self.assertEquals(True,
                          check_not_contain_reserved_url_params(
                              'http://example.org/this?is=a&sane=url'
                          )
                          )
        self.assertEquals(True,
                          check_not_contain_reserved_url_params(
                              'http://example.org/this?is=still&ok=enddate'
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              'http://example.org/file.ext?startdate=nope'
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              'http://example.org/file.ext?enddate=nope'
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              'http://example.org/file.ext?listformat=nope'
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              'http://example.org/file.ext?subject=nope'
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              'http://example.org/file.ext?predicate=nope'
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              'http://example.org/file.ext?object=nope'
                          )
                          )

    def test_check_http_status_codes(self):
        """
        Test for upper http status codes (Section 4.12).
        """
        self.server.serve({
            '/ressource/exists': {
                'GET': {
                    'headers': [('status', '200 OK')]
                }
            }
        })
        prefix = 'http://localhost:%s' % self.server.port
        self.assertEquals(False,
                          check_http_status_codes(prefix + '/ressource/exists')
                          )

        self.server.serve({
            '/ressource': {
                'GET': {
                    'headers': [('status', '200 OK')]
                }
            },
            '/ressource/does/not/exist/unless/you/cheated': {
                'GET': {
                    'headers': [('status', '404 Not Found')]
                }
            }
        })
        self.assertEquals(True,
                          check_http_status_codes(prefix + '/ressource')
                          )
