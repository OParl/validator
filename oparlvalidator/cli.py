# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import argparse
import sys
from . import version
from .validator import OParlJson
from .crawler import Crawler


def main():
    parser = argparse.ArgumentParser(
        description='Validates an OParl system or OParl documents.')
    parser.add_argument(
        'url', metavar='URL', nargs='?', default=None,
        help='URL of the system to test; omit to read JSON from stdin')
    parser.add_argument(
        '-t', '--type', metavar='type', dest='types',
        default=None, action='append',
        help='Set the document types to be checked '
             '(can be used multiple times)')
    parser.add_argument(
        '-r', '--recursive',
        action='store_true', help='Test the whole system recursively')
    parser.add_argument(
        '-n', '--max-documents', metavar='number', type=int, default=None,
        help='Set max number of documents to test per document type')
    parser.add_argument(
        '-c', '--compact', action='store_true',
        help='Gives a compact error report')
    parser.add_argument(
        '-v', '--oparl-version', metavar='version',
        help=('Set the OParl version. '
              'Currently “1” is the only valid option.'))
    parser.add_argument(
        '-V', '--version', action='version',
        version='%(prog)s ' + version.__version__)
    args = parser.parse_args()
    if not args.url:
        for error in OParlJson(sys.stdin.read()).validate():
            print('ERROR: %s' % error.message)
    else:
        crawler = Crawler(seed_url=args.url, max_documents=args.max_documents,
                          type_whitelist=args.types, recursive=args.recursive)
        for url, error in crawler.run():
            print('ERROR in %s: %s' % (url, error.message))
