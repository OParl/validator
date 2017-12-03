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
import subprocess
import sys
from collections import deque
from pathlib import Path
from threading import Thread
from time import sleep
from urllib.parse import urlparse

import gi
import requests
from requests import HTTPError
from tqdm import tqdm

from .cache import Cache
from .exceptions import EndpointNotReachableException, EndpointIsNotAnOParlEndpointException
from .output import Output
from .utils import get_entity_type_from_object, sha1_hexdigest, get_oparl_version_from_object

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
            if self.network['average_ttl'] == 0:
                self.network['average_ttl'] = r.elapsed
            else:
                self.network['average_ttl'] = (self.network['average_ttl'] + r.elapsed) / 2

            if 'content-encoding' in r.headers and r.headers['content-encoding'] not in self.network[
                'encodings']:
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

class BodyWalker(Thread):
    def __init__(self, client, body, queue):
        super(BodyWalker, self).__init__()
        self.client = client
        self.body = body
        self.queue = queue
        self.done = False
        self.neighbors = []

    def run(self):
        try:
            self.neighbors = self.body.get_neighbors()
        except GLib.Error:
            Output.message('Body {} failed to provide entities', self.body.get_id())
            return

        for neighbor in self.neighbors:
            self.queue.acquire()
            self.queue.put(neighbor)
            self.queue.release()

        Output.message("Fetched {} objects from {}", len(self.neighbors), self.body.get_id())
