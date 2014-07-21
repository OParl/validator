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

from ..validator import OParlJson
from ..schema import SCHEMA_DIR

DATA_DIR = join(dirname(__file__), 'testdata')


class TestSchema(unittest.TestCase):
    # pylint: disable=protected-access

    #
    # Helper functions
    #

    def _safe_load_json_file(self, filename):
        try:
            with open(filename) as json_file:
                return json.load(json_file)
        except (IOError, ValueError) as expr:
            print(expr)
            return None

    def _load_test_file(self, filename):
        return self._safe_load_json_file(join(DATA_DIR, filename))

    def _do_test_json_validation(self, obj_type, testfile):
        data = self._load_test_file(testfile)
        self.assertIsNotNone(data,
                             "test data '%s' not found or invalid" % testfile)
        return OParlJson._validate_schema(obj_type, data)

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

    def _test_missing_item(self, obj_type, filename, missing_items):
        """
        This is a shortcut for testing for missing properties in the
        testdata. The verification is expected to fail and all
        supplied "missing_items" are expected as error messages.
        """
        expected_errors = ['%s.*is a required property' %
                           missing for missing in missing_items]
        self._test_validation(obj_type, filename, expected_errors)

    #
    # Real tests
    #

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
        self.assertEquals(OParlJson._build_object_type('oparl:Document'),
                          'oparl:Document')
        self.assertEquals(OParlJson._build_object_type('document'),
                          'oparl:Document')
        self.assertEquals(OParlJson._build_object_type('Document'),
                          'oparl:Document')
        self.assertEquals(OParlJson._build_object_type('DOCUMENT'),
                          'oparl:Document')
        self.assertEquals(OParlJson._build_object_type('oparl:document'),
                          'oparl:document')
        self.assertEquals(OParlJson._build_object_type('agenda_item'),
                          'oparl:AgendaItem')

    def test_valid_agenda(self):
        self._test_validation('oparl:AgendaItem', 'agenda_item.valid.json')

    def test_valid_body(self):
        self._test_validation('oparl:Body', 'body.valid.json')

    def test_valid_consultation(self):
        self._test_validation('oparl:Consultation', 'consultation.valid.json')

    def test_valid_document(self):
        self._test_validation('oparl:Document', 'document.valid.json')

    def test_valid_meeting(self):
        self._test_validation('oparl:Meeting', 'meeting.valid.json')

    def test_valid_organization(self):
        self._test_validation('oparl:Organization', 'organization.valid.json')

    def test_valid_paper(self):
        self._test_validation('oparl:Paper', 'paper.valid.json')

    def test_valid_person(self):
        self._test_validation('oparl:Person', 'person.valid.json')

    def test_valid_system(self):
        self._test_validation('oparl:System', 'system.valid.json')

    def test_invalid_agenda(self):
        self._test_missing_item(
            'oparl:AgendaItem',
            'agenda_item.missing.type.json',
            ['type'])

    def test_invalid_body(self):
        self._test_missing_item(
            'oparl:Body',
            'body.missing.system_paper_member_meeting_organization.json',
            ['system', 'paper', 'member', 'meeting', 'organization'])

    def test_invalid_consultation(self):
        self._test_missing_item(
            'oparl:Consultation',
            'consultation.missing.paper_organization_agendaitem.json',
            ['paper', 'organization', 'agendaItem'])

    def test_invalid_document(self):
        self._test_missing_item(
            'oparl:Document',
            'document.missing.fileName_mimeType_date_'
            'modified_size_accessUrl.json',
            ['fileName', 'mimeType', 'date', 'modified',
             'size', 'accessUrl'])

    def test_invalid_meeting(self):
        self._test_missing_item(
            'oparl:Meeting',
            'meeting.missing.start_organization_participant.json',
            ['start', 'organization', 'participant'])

    def test_invalid_membership(self):
        self._test_missing_item(
            'oparl:Membership',
            'membership.missing.person_organization.json',
            ['person', 'organization'])

    def test_invalid_organization(self):
        self._test_missing_item(
            'oparl:Organization',
            'organization.missing.body_nameLong_member.json',
            ['body', 'nameLong', 'member'])

    def test_invalid_paper(self):
        self._test_missing_item(
            'oparl:Paper',
            'paper.missing.name_body.json',
            ['name', 'body'])

    def test_invalid_person(self):
        self._test_missing_item(
            'oparl:Person',
            'person.missing.name.json',
            ['name'])

    def test_invalid_system(self):
        self._test_missing_item(
            'oparl:System',
            'system.missing.oparlVersion_bodies.json',
            ['oparlVersion', 'bodies'])
