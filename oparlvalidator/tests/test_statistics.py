# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unittest
from ..statistics import with_stats


class TestSchema(unittest.TestCase):

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
