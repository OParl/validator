# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import argparse
import sys
from . import version, crawler
from .validator import OParl


def main():
    parser = argparse.ArgumentParser(description='''
	Validates a OParl system or OParl documents. To test the
	whole system pass the system URL without any arguments.
	''')
    parser.add_argument('url', metavar='URL',
        help='URL of the system to test; - for stdin')
    parser.add_argument('-t', '--type', metavar='type', dest='types',
        default=None, action='append',
        help='set the document types that should be checked '
             '(could be used multiple times)')
    parser.add_argument('-a', '--all', dest='whole_system',
        action='store_true', help='test the whole system')
    parser.add_argument('-n', '--max-documents', metavar='number', type=int,
        dest='num_docs', default=None,
        help='set max number of documents to test per document type')
    parser.add_argument('-c', '--compact', action='store_true',
        dest='compact', help='gives a compact error report')
    parser.add_argument('-v', '--set-version', metavar='version',
        dest='version', help=('set the OParl version. '
                              'Currently "1" is the only valid option.'))
    parser.add_argument('-V', '--version', action='version',
        version='%(prog)s ' + version.__version__)
    args = parser.parse_args()
    if args.url == '-':
        try:
            OParl(sys.stdin.read()).validate()
            print('Valid!')
        # TODO: define proper Exceptions for the Validator
        except ValueError as e:
            print('JSON error: ' + str(e))
        except Exception as e:  # exception from jsonschema validator
            path = ''
            if(len(e.path) > 0):
                path = '.'.join(e.path)
                path = '"{}": '.format(path)
            error_msg = path + e.message
            print(error_msg)
    else:
        crawler.Crawler(args.url, args.types, args.whole_system).validate(args.num_docs)
