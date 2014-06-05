# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os.path
import unittest
from ..validator import OParl


class TestSchema(unittest.TestCase):

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), 'data.json')
        with open(path) as json_file:
            self.sample_object = json_file.read()

    def test_sample_object_validates(self):
        self.assertTrue(OParl(self.sample_object).validate())

    def test_spec_version(self):
        """
        oparl:System.oparlVersion must equal http://oparl.org/specs/1.0/
        """
        pass    # TODO: [RB|Jun 5, 2014|todo] implement

    def test_must_have_mailto_prefix(self):
        """
        email address must be prefixed with "mailto:"
        """
        pass    # TODO: [RB|Jun 5, 2014|todo] implement

    def test_is_valid_email(self):
        """
        check for valid email address
        """
        pass    # TODO: [RB|Jun 5, 2014|todo] implement