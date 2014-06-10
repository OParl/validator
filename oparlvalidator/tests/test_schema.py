# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unittest
import json
from collections import defaultdict
from os import listdir
from os.path import join, dirname
from ..validator import OParl
from jsonschema.exceptions import ValidationError, SchemaError

DATA_DIR = join(dirname(__file__), 'testdata')


class TestSchema(unittest.TestCase):
    # pylint: disable=protected-access

    def _load_testdata(self):
        testdata = defaultdict(list)
        key = lambda filename: filename.split('.', 1)[0]
        filenames = [name for name in listdir(DATA_DIR)
                     if name.endswith('.json')]
        for filename in filenames:
            with open(join(DATA_DIR, filename)) as json_file:
                testdata[key(filename)].append(json.load(json_file))
        return testdata

    def setUp(self):
        self.testdata = self._load_testdata()
        self.oparl = OParl()

    def test_build_object_type(self):
        self.assertEquals(self.oparl._build_object_type('oparl:Document'),
                          'oparl:Document')
        self.assertEquals(self.oparl._build_object_type('document'),
                          'oparl:Document')
        self.assertEquals(self.oparl._build_object_type('Document'),
                          'oparl:Document')
        self.assertEquals(self.oparl._build_object_type('DOCUMENT'),
                          'oparl:Document')
        self.assertEquals(self.oparl._build_object_type('oparl:document'),
                          'oparl:document')
        self.assertEquals(self.oparl._build_object_type('agenda_item'),
                          'oparl:AgendaItem')

    def test_json_validation(self):
        for obj_type in self.testdata:
            validator = self.oparl._get_validator(obj_type)
            self.assertIsNotNone(
                validator,
                'Could not get validator for object type: %s' % obj_type)
            for structure in self.testdata[obj_type]:
                try:
                    validator.validate(structure)
                except (ValidationError, SchemaError) as e:
                    self.assertTrue(False, 'Validation failed: %s' % e)
