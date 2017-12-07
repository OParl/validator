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

import requests

from core.check import Check, CheckResult

class CheckFileReachability (Check):
    def evaluates_entity_type(self):
        return 'file'

    def evaluate(self, entity):
        results = []

        results.join(self.check_access_url(entity))
        results.join(self.check_download_url(entity))

        return results

    def check_access_url(self, entity):
        results = []

        if entity.get_access_url() is None:
            results.append(CheckResult('error', 'Object is missing an access url'))
            return results

        try:
            head = requests.head(entity.get_access_url())
        except requests.exceptions.RequestException:
            results.append(CheckResult('warning', 'Failed to connect to access url'))
            return results

        return results

    def check_download_url(self, entity):
        results = []

        if entity.get_download_url() is None:
            results.append(CheckResult('info', 'It is recommended to provide a separate download url'))
            return results

        try:
            head = requests.head(entity.get_download_url())
        except requests.exceptions.RequestException:
            results.append(CheckResult('warning', 'Failed to connect to download url'))
            return results

        if 'content-disposition' not in head.headers:
            results.append('warning', 'Download url should have a Content-Disposition header')

        return results