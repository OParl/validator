# -*- encoding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import unittest
from .. import version


class TestVersion(unittest.TestCase):

    def test_version_exists(self):
        self.assertTrue('__version__' in version.__dict__)

    def test_version_contains_2_dots(self):
        self.assertEquals(2, len([c for c in version.__version__ if '.' == c]))
