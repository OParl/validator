# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unittest
from ..statistics import with_stats


class TestStatistics(unittest.TestCase):

    def setUp(self):
        @with_stats
        def init(stats=None):
            # we do not want to change the arguments from the
            # overwritten method, so we wrap this here again
            stats.initialize()

        init()

    @with_stats
    def test_init(self, stats=None):
        self.assertEquals(0, stats.num_docs)

    @with_stats
    def test_count_docs(self, stats=None):
        stats.count_document()
        stats.count_document()
        stats.count_document()
        self.assertEquals(3, stats.num_docs)

    @with_stats
    def test_count_types(self, stats=None):
        stats.count_type('a')
        stats.count_type('a')
        stats.count_type('b')
        self.assertEquals({'a': 2, 'b': 1}, dict(stats.num_docs_per_type))

    def test_return(self):
        @with_stats
        def stats(stats=None):
            stats.count_document()
            self.assertEquals(1, stats.num_docs)
            return 'test'
        self.assertEquals('test', stats())

    @with_stats
    def test_reinit(self, stats=None):
        stats.count_document()
        stats.count_type('a')
        self.assertEquals(1, stats.num_docs)
        self.assertEquals({'a': 1}, dict(stats.num_docs_per_type))
        stats.initialize()
        self.assertEquals({}, dict(stats.num_docs_per_type))
        self.assertEquals(0, stats.num_docs)
