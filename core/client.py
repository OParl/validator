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

from urllib.parse import urlparse

import gi
import requests
from requests import HTTPError

from .body_walker import BodyWalker
from .cache import Cache
from .exceptions import EndpointNotReachableException, EndpointIsNotAnOParlEndpointException
from .output import Output

gi.require_version('OParl', '0.2')
from gi.repository import OParl
from gi.repository import GLib

class Client:
    """
        The client wrapping liboparl- and general endpoint communication
    """
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.network = {
            'ssl': False,
            'average_ttl': 0,
            'encodings': []
        }

        if not self.is_reachable():
            raise EndpointNotReachableException()

        self.check_ssl()

        self.cache = Cache()

        self.client = OParl.Client()
        self.client.set_strict(False)

        self.client.connect('resolve_url', self.resolve_url)

        self.open_client()

    def resolve_url(self, client, url):
        if url is None:  # This is from objects liboparl failed to resolve!
            return None

        if not self.cache.has(url):
            r = requests.get(url, verify=self.network['ssl'])

            try:
                r.raise_for_status()
            except HTTPError:
                return OParl.ResolveUrlResult(resolved_data=None, success=False, status_code=-1)

            self.cache.set(url, r.text)

            # TODO: should probably switch this code over to a moving average of a few (all?) requests
            # TODO: should track ttl of cached requests to make this more accurate
            if self.network['average_ttl'] == 0:
                self.network['average_ttl'] = r.elapsed
            else:
                self.network['average_ttl'] = (self.network['average_ttl'] + r.elapsed) / 2

            if 'content-encoding' in r.headers and \
                r.headers['content-encoding'] not in self.network['encodings']:
                self.network['encodings'].append(r.headers['content-encoding'])

            return OParl.ResolveUrlResult(resolved_data=r.text, success=True, status_code=r.status_code)
        else:
            return OParl.ResolveUrlResult(resolved_data=self.cache.get(url), success=True, status_code=-1)

    def is_reachable(self):
        try:
            r = requests.head(self.endpoint)
            return r.status_code in [200, 304]
        except requests.exceptions.RequestException:
            return False

    def check_ssl(self):
        # TODO: this feels very much incorrect to me
        try:
            requests.get(self.endpoint)

            components = urlparse(self.endpoint)
            if components.scheme != 'http':
                self.network['ssl'] = True
        except requests.exceptions.SSLError:
            pass

    def open_client(self):
        try:
            self.system = self.client.open(self.endpoint)
        except GLib.Error:
            raise EndpointIsNotAnOParlEndpointException()

    def create_body_walker(self, body, queue):
        return BodyWalker(self.client, body, queue)
