"""
The MIT License (MIT)

Copyright (c) 2017 Stefan Graupner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from json import dumps
import sys

from tqdm import tqdm

def print_json_patch(json):
    print(dumps(json, separators=(',', ':')), file=sys.stderr)

class Output:
    porcelain = False
    progress_bars = {}
    silent = False
    verbosity = 0

    @staticmethod
    def initialize(porcelain = False, silent = False, verbosity = 0):
        Output.porcelain = porcelain
        Output.silent = silent
        Output.verbosity = verbosity

        if porcelain and not silent:
            print_json_patch({
                'messages': [],
                'progress_bars': {}
            })

    @staticmethod
    def message(message, *args):
        """ Prints a general message to stdout """
        if Output.silent:
            return

        formatted = message

        if args:
            formatted = message.format(*args)

        if Output.porcelain:
            patch = [
                {
                    'op': 'add',
                    'path': '/messages/-',
                    'value': formatted
                }
            ]

            print_json_patch(patch)
        else:
            print(formatted, file=sys.stderr)

    @staticmethod
    def exception(exception):
        # TODO: custom exception output for porcelain mode
        Output.message(exception)

    @staticmethod
    def add_progress_bar(id, desc, unit = 'Objects'):
        if Output.silent:
            return

        if Output.porcelain:
            Output.progress_bars[id] = {
                'desc': desc,
                'unit': unit,
                'remaining': 0,
                'current': 0
            }

            patch = [
                {
                    'op': 'add',
                    'path': '/progress_bars/{}'.format(id),
                    'value': Output.progress_bars[id]
                }
            ]

            print_json_patch(patch)
        else:
            # FIXME: tqdm does not appear to be thread safe
            pass
            # unit = ' ' + unit

            # Output.progress_bars[id] = tqdm(
            #     desc=desc,
            #     total=9e9,
            #     unit=unit,
            #     file=sys.stderr
            # )

    @staticmethod
    def update_progress_bar(id, remaining=9e9):
        if Output.silent:
            return

        if Output.porcelain:
            Output.progress_bars[id]['remaining'] = remaining
            Output.progress_bars[id]['current'] += 1

            patch = [
                {
                    'op': 'replace',
                    'path': '/progress_bars/{}'.format(id),
                    'value': Output.progress_bars[id]
                }
            ]

            print_json_patch(patch)
        else:
            # Output.progress_bars[id].update()
            pass