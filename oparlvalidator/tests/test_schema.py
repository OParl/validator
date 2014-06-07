# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
import unittest
from os.path import join, dirname
from ..validator import OParl


class TestSchema(unittest.TestCase):

    def setUp(self):
        # FIXME: We might want to split the JSON file up,
        # but since it’s buggy anyway, I won’t do that now.
        path = join(dirname(__file__), 'testdata', 'data.json')
        with open(path) as json_file:
            self.sample_structures = []
            structures = json.load(json_file).values()
            for structure in structures:
                assert type(structure) in (list, dict)
                if type(structure) == list:
                    self.sample_structures.extend(structure)
                else:
                    self.sample_structures.append(structure)
            self.sample_structures = sorted(
                map(json.dumps, self.sample_structures))

    @unittest.skip('We need better test data')
    def test_sample_objects_validates(self):
        for structure in self.sample_structures:
            self.assertTrue(OParl(structure).validate())


