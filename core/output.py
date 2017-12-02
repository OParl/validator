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

import json

class Output(object):
    porcelain = False
    silent = False
    progress_bars = {}

    @staticmethod
    def initialize():
        if not Output.porcelain or Output.silent:
            return

        print(json.dumps({
            'messages': [],
            'progress_bars': {}
        }))

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

            formatted = json.dumps(patch)

        print(formatted)

    @staticmethod
    def add_progress_bar(id, desc = '', unit = 'Objects'):
        if Output.silent:
            return

        if Output.porcelain:
            Output.progress_bars[id] = {
                'desc': desc,
                'unit': unit,
                'total': None,
                'current': 0
            }

            patch = [
                {
                    'op': 'add',
                    'path': '/progress_bars/{}'.format(id),
                    'value': Output.progress_bars[id]
                }
            ]

            print(json.dumps(patch))
        else:
            desc = 'Validating Object "{}"'.format(object.get_id())
            unit = ' ' + unit

            Output.progres_bars[id] = tqdm(
                desc=desc,
                total=9e9,
                unit=unit
            )

    @staticmethod
    def update_progress_bar(id, total=9e9):
        if Output.silent:
            return

        if Output.porcelain:
            Output.progress_bars[id]['total'] = total
            Output.progress_bars[id]['current'] += 1

            patch = [
                {
                    'op': 'replace',
                    'path': '/progress_bars/{}'.format(id),
                    'value': Output.progress_bars[id]
                }
            ]

            print(json.dumps(patch))
        else:
            Output.progress_bars[id].update()