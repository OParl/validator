# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unittest
import json
from os.path import join, dirname
from ..validator import OParl
from jsonschema.exceptions import ValidationError, SchemaError

DATA_DIR = join(dirname(__file__), 'testdata')


class TestSchema(unittest.TestCase):
    # pylint: disable=protected-access

    def setUp(self):
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

    def _load_test_file(self, filename):
        try:
            with open(join(DATA_DIR, filename)) as json_file:
                return json.load(json_file)
        except IOError:
            return None

    def _do_test_json_validation(self, obj_type, testfile):
        data = self._load_test_file(testfile)
        self.assertIsNotNone(data, "test data '%s' not found" % testfile)

        validator = self.oparl._get_validator(obj_type)
        self.assertIsNotNone(
            validator,
            'Could not get validator for object type: %s' % obj_type)
        validator.validate(data)
        return True

    def _test_validation_ok(self, obj_type, testfile):
        try:
            self._do_test_json_validation(obj_type, testfile)
        except (ValidationError, SchemaError) as e:
            self.assertTrue(False, 'Validation failed: %s' % e)

    def _test_validation_fail(self, obj_type, testfile, error):
        try:
            self._do_test_json_validation(obj_type, testfile)
            self.assertTrue(False, 'Validation of %s is expected to fail, '
                            'but did not.' % testfile)
        except (ValidationError, SchemaError) as e:
            self.assertRegexpMatches(e.message, error,
                                     'Unexpected error message')

    def test_valid_json_validation(self):
        self._test_validation_ok('oparl:AgendaItem',
                                 'agenda_item.valid.json')
        self._test_validation_ok('oparl:Body',
                                 'body.valid.json')
        self._test_validation_ok('oparl:Consultation',
                                 'consultation.valid.json')
        self._test_validation_ok('oparl:Document',
                                 'document.valid.json')
        self._test_validation_ok('oparl:Meeting',
                                 'meeting.valid.json')
        self._test_validation_ok('oparl:Organization',
                                 'organization.valid.json')
        self._test_validation_ok('oparl:Paper',
                                 'paper.valid.json')
        self._test_validation_ok('oparl:Person',
                                 'person.valid.json')
        self._test_validation_ok('oparl:System',
                                 'system.valid.json')

    def test_json_validation_failures(self):
        self._test_validation_fail('oparl:AgendaItem',
                                   'agenda_item.missing_type.json',
                                   'type.*is a required property')
