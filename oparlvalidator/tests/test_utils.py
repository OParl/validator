# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unittest
from os.path import join
from .. import utils


class TestUtils(unittest.TestCase):
    # pylint: disable=protected-access

    def test_build_object_type(self):
        self.assertEquals(
            utils.build_object_type('http://oparl.org/schema/1.0/Document'),
            'schema/1.0/Document')
        self.assertEquals(
            utils.build_object_type('schema/1.0/Document'),
            'schema/1.0/Document')
        self.assertEquals(
            utils.build_object_type(
                join(utils.SCHEMA_DIR, '1.0', 'Document')),
            'schema/1.0/Document')
        self.assertEquals(
            utils.build_object_type(
                join(utils.SCHEMA_DIR, '1.0', 'Document.json')),
            'schema/1.0/Document')
        self.assertEquals(
            utils.build_object_type(
                join(utils.SCHEMA_DIR, '1.0', 'AgendaItem.json')),
            'schema/1.0/AgendaItem')
