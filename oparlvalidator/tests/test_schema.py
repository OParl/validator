# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
import re
import unittest
from collections import defaultdict
from os import listdir
from os.path import join, dirname
from ..validator import OParl

DATA_DIR = join(dirname(__file__), 'testdata')

class TestSchema(unittest.TestCase):

    def setUp(self):
        self.testdata = defaultdict(list)
        key = lambda filename: filename.split('.', 1)[0]
        filenames = [name for name in listdir(DATA_DIR)
                     if name.endswith('.json')]
        for filename in filenames:
            with open(join(DATA_DIR, filename)) as json_file:
                self.testdata[key(filename)].append(json_file.read())

    def test_agendaitem_validates(self):
        for structure in self.testdata['agendaitem']:
            self.assertTrue(OParl(structure).validate())

    def test_body_validates(self):
        for structure in self.testdata['body']:
            self.assertTrue(OParl(structure).validate())

    def test_consultation_validates(self):
        for structure in self.testdata['consultation']:
            self.assertTrue(OParl(structure).validate())

    def test_document_validates(self):
        for structure in self.testdata['document']:
            self.assertTrue(OParl(structure).validate())

    def test_meeting_validates(self):
        for structure in self.testdata['meeting']:
            self.assertTrue(OParl(structure).validate())

    def test_membership_validates(self):
        for structure in self.testdata['membership']:
            self.assertTrue(OParl(structure).validate())

    def test_organization_validates(self):
        for structure in self.testdata['organization']:
            self.assertTrue(OParl(structure).validate())

    def test_paper_validates(self):
        for structure in self.testdata['paper']:
            self.assertTrue(OParl(structure).validate())

    def test_person_validates(self):
        for structure in self.testdata['person']:
            self.assertTrue(OParl(structure).validate())

    def test_system_validates(self):
        for structure in self.testdata['system']:
            self.assertTrue(OParl(structure).validate())
