# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unittest
import json
import re
import glob
from os.path import join, dirname
from jsonschema.validators import Draft4Validator
import jsonschema.exceptions

from ..validator import OParl
from ..schema import SCHEMA_DIR

DATA_DIR = join(dirname(__file__), 'testdata')


class TestSchema(unittest.TestCase):
    # pylint: disable=protected-access

    def _safe_load_json_file(self, filename):
        try:
            with open(filename) as json_file:
                return json.load(json_file)
        except (IOError, ValueError):
            return None

    def _load_test_file(self, filename):
        return self._safe_load_json_file(join(DATA_DIR, filename))

    def test_validate_schema(self):
        def _validate(filename):
            try:
                data = self._safe_load_json_file(filename)
                self.assertIsNotNone(data, '%s: invalid json syntax' %
                                     filename)
                Draft4Validator(Draft4Validator.META_SCHEMA).validate(data)
            except (jsonschema.exceptions.ValidationError,
                    jsonschema.exceptions.SchemaError) as excp:
                self.assertTrue(False, '%s: oparl schema invalid: %s' %
                                (filename, excp))

        for schema_file in glob.glob(join(SCHEMA_DIR, '*.json')):
            _validate(schema_file)

    def test_build_object_type(self):
        self.assertEquals(OParl._build_object_type('oparl:Document'),
                          'oparl:Document')
        self.assertEquals(OParl._build_object_type('document'),
                          'oparl:Document')
        self.assertEquals(OParl._build_object_type('Document'),
                          'oparl:Document')
        self.assertEquals(OParl._build_object_type('DOCUMENT'),
                          'oparl:Document')
        self.assertEquals(OParl._build_object_type('oparl:document'),
                          'oparl:document')
        self.assertEquals(OParl._build_object_type('agenda_item'),
                          'oparl:AgendaItem')

    def _do_test_json_validation(self, obj_type, testfile):
        data = self._load_test_file(testfile)
        self.assertIsNotNone(data,
                             "test data '%s' not found or invalid" % testfile)
        return OParl._validate_schema(obj_type, data)

    def _test_validation(self, obj_type, testfile, expected_errors=None):
        """
        Check validation results. "expected_errors" contains patterns
        for matching the error messages retuned by the validation. All
        returned messages should match on supplied item and all
        supplied items should match one returned error message. So if
        no "expected_errors" are supplied, the validation should
        pass.
        """

        if expected_errors is None:
            expected_errors = list()

        for error in self._do_test_json_validation(obj_type, testfile):
            for expected_error in expected_errors:
                if re.search(expected_error, error.message):
                    expected_errors.remove(expected_error)
                    break
            else:
                self.assertTrue(False, '%s: Unexpected error message: "%s"' %
                                (testfile, error.message))
        if len(expected_errors) > 0:
            self.assertTrue(False,
                            '%s: Missing some expected error messages: %s' %
                            (testfile, expected_errors))

    def test_valid_json_validation(self):
        """
        This tests some validation. All this validation should pass
        and no errors should be returned.
        """
        self._test_validation('oparl:AgendaItem', 'agenda_item.valid.json')
        self._test_validation('oparl:Body', 'body.valid.json')
        self._test_validation('oparl:Consultation', 'consultation.valid.json')
        self._test_validation('oparl:Document', 'document.valid.json')
        self._test_validation('oparl:Meeting', 'meeting.valid.json')
        self._test_validation('oparl:Organization', 'organization.valid.json')
        self._test_validation('oparl:Paper', 'paper.valid.json')
        self._test_validation('oparl:Person', 'person.valid.json')
        self._test_validation('oparl:System', 'system.valid.json')

    def test_json_validation_failures(self):
        """
        This tests some validation failures and check the returned
        error messages, if they match some expected patterns.
        """

        def _test_missing_item(obj_type, filename, missing_items):
            """
            This is a shortcut for testing for missing properties in
            the testdata. The verification is expected to fail and all
            supplied "missing_items" are expected as error messages.
            """
            expected_errors = ['%s.*is a required property' %
                               missing for missing in missing_items]
            self._test_validation(obj_type, filename, expected_errors)

        _test_missing_item(
            'oparl:AgendaItem',
            'agenda_item.missing.type.json',
            ['type'])
        _test_missing_item(
            'oparl:Body',
            'body.missing.system_paper_member_meeting_organization.json',
            ['system', 'paper', 'member', 'meeting', 'organization'])
        _test_missing_item(
            'oparl:Consultation',
            'consultation.missing.committee_agendaItem_paper.json',
            ['committee', 'agendaItem', 'paper'])
        _test_missing_item(
            'oparl:Document',
            'document.missing.fileName_mimeType_date_'
            'modified_size_accessUrl.json',
            ['fileName', 'mimeType', 'data', 'modified',
             'size', 'accessUrl'])
        _test_missing_item(
            'oparl:Meeting',
            'meeting.missing.start_organization.json',
            ['start', 'organization'])
        _test_missing_item(
            'oparl:Membership',
            'membership.missing.person_organization.json',
            ['person', 'organization'])
        _test_missing_item(
            'oparl:Organization',
            'organization.missing.body_nameLong_member.json',
            ['body', 'nameLong', 'member'])
        _test_missing_item(
            'oparl:Paper',
            'paper.missing.name_body.json',
            ['name', 'body'])
        _test_missing_item(
            'oparl:Person',
            'person.missing.name.json',
            ['name'])
        _test_missing_item(
            'oparl:System',
            'system.missing.oparlVersion_bodies.json',
            ['oparlVersion', 'bodies'])
