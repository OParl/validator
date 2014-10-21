# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unittest
from .. import statistics


TEST_SCHEMA = {
    'properties': {'a': None, 'b': None, 'c': None},
    'required': ['a'],
    'oparl:recommended': ['b']
}


class TestStatistics(unittest.TestCase):

    def setUp(self):
        statistics.initialize()

    def test_init(self):
        self.assertEquals(0, statistics.num_docs)

    def test_count_docs(self):
        statistics.count_document()
        statistics.count_document()
        statistics.count_document()
        self.assertEquals(3, statistics.num_docs)

    def test_count_types(self):
        statistics.count_type('a')
        statistics.count_type('a')
        statistics.count_type('b')
        self.assertEquals({'a': 2, 'b': 1}, dict(statistics.num_docs_per_type))

    def test_return(self):
        def stats():
            statistics.count_document()
            self.assertEquals(1, statistics.num_docs)
            return 'test'
        self.assertEquals('test', stats())

    def test_reinit(self):
        statistics.count_document()
        statistics.count_type('a')
        self.assertEquals(1, statistics.num_docs)
        self.assertEquals({'a': 1}, dict(statistics.num_docs_per_type))
        statistics.initialize()
        self.assertEquals({}, dict(statistics.num_docs_per_type))
        self.assertEquals(0, statistics.num_docs)

    def test_count_properties(self):
        statistics.count_properties('test', ['a', 'b', 'c', 'd'], TEST_SCHEMA)
        self.assertEquals(dict(statistics.properties['recommended']),
                          {'test': {'b': 1}})
        self.assertEquals(dict(statistics.properties['optional']),
                          {'test': {'c': 1}})
        self.assertEquals(dict(statistics.properties['custom']),
                          {'test': {'d': 1}})
