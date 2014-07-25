# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import threading
import unittest
import static
from wsgiref.simple_server import make_server
from os.path import join, dirname
from ..crawler import Crawler
from .server import Server
from ..server_tests import check_accecpt_encoding
from ..server_tests import check_not_contain_reserved_url_params
from ..server_tests import check_http_status_codes

DATA_DIR = join(dirname(__file__), 'testdata')


class TestCrawler(unittest.TestCase):
    # pylint: disable=protected-access

    def setUp(self):
        wsgi_app = static.Cling(DATA_DIR)
        self.httpd = make_server('', 2342, wsgi_app)
        httpd_thread = threading.Thread(target=self.httpd.serve_forever)
        httpd_thread.setDaemon(True)
        httpd_thread.start()

    def tearDown(self):
        self.httpd.shutdown()

    def _fix_url(self, crawler, host):
        orig_retrieve = crawler._retrieve

        def _fixUrl(self, *args, **kwargs):
            url = args[0].replace('https://oparl.example.org/', host)
            return orig_retrieve(self, url, **kwargs)
        crawler._retrieve = _fixUrl

    def test_something(self):
        self._fix_url(Crawler, 'http://localhost:2342/')
        # TODO: Improve test data, then raise limit
        Crawler('https://oparl.example.org/person.valid.json',
                max_documents=0).run()

    def test_accept_encoding(self):
        """
        Test for compression support (Section 4.11).
        """
        # setup server
        server = Server()
        test_cases = {
            "/example/valid": {
                "GET":
                {
                    'headers': [('content-encoding', 'gzip')],
                }
            },
            "/example/invalid_empty": {
                "GET":
                {
                    'headers': [('content-encoding', '')],
                }
            },
            "/example/invalid_not_set": {
                "GET":
                {
                    'headers': [],
                }
            },
            "/example/invalid_type_not_supported": {
                "GET":
                {
                    'headers': [('content-encoding', 'esoteric')],
                }
            },
        }
        server.serve(test_cases)

        # run assertions
        prefix = "http://localhost:%s" % server.port
        self.assertEquals(True,
                          check_accecpt_encoding(prefix + "/example/valid"))
        self.assertEquals(False,
                          check_accecpt_encoding(
                              prefix + "/example/invalid_empty"))
        self.assertEquals(False,
                          check_accecpt_encoding(
                              prefix + "/example/invalid_not_set"))
        self.assertEquals(False,
                          check_accecpt_encoding(
                              prefix + "/example/invalid_type_not_supported")
                          )
        server.shutdown()

    def test_invalid_url_params(self):
        """
        Test for reserved key within queries (URLs) (Section 4.13).
        """
        self.assertEquals(True,
                          check_not_contain_reserved_url_params(
                              "http://example.org/this?is=a&sane=url"
                          )
                          )
        self.assertEquals(True,
                          check_not_contain_reserved_url_params(
                              "http://example.org/this?is=still&ok=enddate"
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              "http://example.org/file.ext?startdate=nope"
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              "http://example.org/file.ext?enddate=nope"
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              "http://example.org/file.ext?listformat=nope"
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              "http://example.org/file.ext?subject=nope"
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              "http://example.org/file.ext?predicate=nope"
                          )
                          )
        self.assertEquals(False,
                          check_not_contain_reserved_url_params(
                              "http://example.org/file.ext?object=nope"
                          )
                          )

    def test_check_http_status_codes(self):
        """
        Test for upper http status codes (Section 4.12).
        """
        # setup server
        server = Server()
        server.serve({
            "/ressource/exists": {
                "GET": {
                    "headers": [("status", "200 OK")]
                }
            }
        })
        prefix = "http://localhost:%s" % server.port
        self.assertEquals(False,
                          check_http_status_codes(prefix + "/ressource/exists")
                          )

        server.serve({
            "/ressource": {
                "GET": {
                    "headers": [("status", "200 OK")]
                }
            },
            "/ressource/does/not/exist/unless/you/cheated": {
                "GET": {
                    "headers": [("status", "404 Not Found")]
                }
            }
        })
        self.assertEquals(True,
                          check_http_status_codes(prefix + "/ressource")
                          )
        server.shutdown()
