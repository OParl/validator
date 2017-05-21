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
import hashlib
import datetime
from pathlib import Path
from collections import deque

import requests
from tqdm import tqdm

import gi
gi.require_version('OParl', '0.2')

from gi.repository import OParl
from gi.repository import GLib

from src.cache import Cache, RedisCache
from src.result import Result

VALID_OPARL_VERSIONS = [
    "https://schema.oparl.org/1.0/"
]


class Validator(object):
    """
        This is the Validator base class
    """
    url = ""
    schema_cache = {}
    client = None
    cache = None
    options = None
    result = None
    seen = []
    current_object = None
    object_count = 0

    def __init__(self, url, options):
        # warn the user that schema validation is not yet implemented
        # TODO: this code should be removed eventually
        if options.validate_schema:
            print("Schema validation is not implemented yet and will be skipped.")

        self.url = url
        self.options = options

        if not self.is_reachable_uri(url):
            print("Endpoint {} is not reachable, aborting validation.".format(url))
            exit(1)

        self.client = OParl.Client()
        self.client.set_strict(False)

        self.client.connect("resolve_url", self.resolve_url)
        self.client.connect("shit_happened", self.cleanup_occured_excrement)

        mode = Result.Mode.Human

        if options.format == 'json':
            mode = Result.Mode.Json

        self.result = Result(silent=options.silent, mode=mode, verbosity=options.verbosity)

        if options.redis:
            self.cache = RedisCache()
        else:
            self.cache = Cache()

    def resolve_url(self, client, url, status):
        try:
            if url == "unknown id": # This is from objects liboparl failed to resolve!
                return None
            if not self.cache.has(url):
                r = requests.get(url)
                r.raise_for_status()

                self.cache.set(url, r.text)
                status = r.status_code

                return r.text
            else:
                text = self.cache.get(url)
                status = 304 # report as not modified because cache hit

                return str(text, 'utf-8')
        except Exception as e:
            return None

    def validate(self):
        if self.options.validate_schema:
            version = system.get_oparl_version()

            if version in VALID_OPARL_VERSIONS:
                self.check_schema_cache(version)

        system = self.client.open(self.url)
        self.print("Validating {}", self.url)
        self.validate_object(system)
        self.object_count = 1

        bodies = system.get_body()
        self.object_count += len(bodies)

        for body in bodies:
            self.validate_object(body)
            self.validate_neighbors(body)

        # if self.options.save_results:
        #     # TODO: Reimplement result saving
        #     pass

    def validate_neighbors(self, object):
        neighbors = deque(self.get_unseen_neighbors(object))
        neighbors_count = len(neighbors)

        self.object_count += neighbors_count

        if self.options.silent:
            progress_bar = None
        else:
            progress_bar = tqdm(desc='Validating Body "{}"'.format(object.get_name()), total=9e9, unit=' Objects')

        while len(neighbors) > 0:
            neighbor = neighbors.popleft()
            self.validate_object(neighbor)

            additional_neighbors = self.get_unseen_neighbors(object)
            additional_neighbors_count = len(additional_neighbors)
            if additional_neighbors_count > 0:
                neighbors.extend(additional_neighbors)
                neighbors_count += additional_neighbors_count
                self.object_count += additional_neighbors_count

            if type(progress_bar) == tqdm:
                progress_bar.total = neighbors_count
                progress_bar.update()


    def validate_object(self, object):
        """ Validate a single object """
        self.current_object = object

        hash = self.get_object_hash(object)
        if hash in self.seen:
            return
        else:
            self.seen.append(hash)

        try:
            validation_results = object.validate()

            for validation_result in validation_results:
                self.parse_validation_result(validation_result)
        except GLib.Error as e:
            pass

        if object is OParl.File:
            print("Found a file!")

    def get_unseen_neighbors(self, object):
        unseen_neighbors = []

        try:
            object_neighbors = object.get_neighbors()
        except GLib.Error:
            # TODO: track objects that should have had neighbors
            pass

        for neighbor in object_neighbors:
            hash = self.get_object_hash(neighbor)
            if hash not in self.seen:
                unseen_neighbors.append(neighbor)

        return unseen_neighbors

    def get_object_hash(self, object, object_id = None):
        """ Compute the hash with which the an object is tracked by the validator """

        if object != None:
            try:
                object_id = object.get_id()
            except GLib.Error as e:
                return None

        if object_id == None:
            # TODO: track invalid object id
            return None

        return hashlib.sha1(object_id.encode('ascii')).hexdigest()

    def get_schema_for_type(self, type):
        """ Get the schema for an entity """
        print(type)

    def cleanup_occured_excrement(self, client, excrement):
        """ Process the shit happened signal from liboparl """
        self.parse_validation_result(excrement)

    def parse_validation_result(self, validation_result):
        """ Parse a liboparl ValidationResult into a validator message """
        if self.get_object_hash(None, validation_result.get_object_id()) in self.seen:
            return

        severity = validation_result.get_severity()
        description = validation_result.get_description()

        if severity == OParl.ErrorSeverity.INFO:
            pass
        if severity == OParl.ErrorSeverity.WARNING:
            pass
        if severity == OParl.ErrorSeverity.ERROR:
            pass

    def check_schema_cache(self, schema_version):
        """ Updates the schema cache for the given version """
        schema_path = Path("schema_cache/{}".format(hashlib.sha1(schema_version.encode('ascii')).hexdigest()))
        schema_path.mkdir(parents=True, exist_ok=True)

        schema_listing = requests.get(schema_version).json()

        for schema in schema_listing:
            entity_path = schema_path / \
                hashlib.sha1(schema.encode('ascii')).hexdigest()
            if entity_path.exists():
                with open(entity_path, 'r') as f:
                    self.schema_cache[schema] = json.loads(f.read())

            else:
                self.schema_cache[schema] = requests.get(schema).json()
                with open(entity_path, 'w') as f:
                    f.write(json.dumps(self.schema_cache[schema]))

    def is_reachable_uri(self, uri):
        try:
            r = requests.head(uri)
            return r.status_code in [200, 304]
        except requests.exceptions.ConnectionError:
            return False

    def print(self, message, *args):
        if not self.options.silent:
            print(message.format(*args))