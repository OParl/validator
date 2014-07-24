# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import threading
import unittest
import static
from wsgiref.simple_server import make_server
from os.path import join, dirname
from ..crawler import Crawler

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

    def test_invalid_url_params(self):
        """
        Test for invalid URL parameters which can be found in section 4.13.
        """
        # TODO: implement
        pass
