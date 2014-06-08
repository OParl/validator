import unittest
import pep8
import os
import sys

from pylint import lint
from pylint.reporters.text import TextReporter


class CodeStyleTest(unittest.TestCase):
    top = os.path.join(os.path.dirname(__file__), '..')

    def test_pep8(self):
        pep8style = pep8.StyleGuide()
        result = pep8style.check_files([os.path.abspath(self.top)])
        self.assertEqual(result.total_errors, 0,
                         "Pep8 found code style errors.")

    def test_pylint(self):
        rcfile = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              'pylint.rc'))
        args = ['--rcfile=' + rcfile, self.top]
        reporter = TextReporter(output=sys.stdout)
        result = lint.Run(args=args, reporter=reporter, exit=False)
        self.assertEqual(result.linter.msg_status, 0,
                         "Pylint found code style errors.")
