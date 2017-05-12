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
import requests

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
        try:
            system = self.client.open(self.url)
            self.validate_object(system)
        except GLib.Error as e:
            print(e)
            exit()

        if self.options.validate_schema:
            version = system.get_oparl_version()

            msg = "Detected OParl Version {}"
            if version in VALID_OPARL_VERSIONS:
                self.check_schema_cache(version)

        if self.options.save_results:
            # TODO: Reimplement result saving
            pass

    def validate_neighbors(self, neighbors):
        sub_neighbors = []

        for neighbor in neighbors:
            try:
                self.validate_object(neighbor)
                sub_neighbors.extend(neighbor.get_neighbors())
            except GLib.Error as e:
                continue
            except TypeError as e:
                print(e)
                exit()

        if len(sub_neighbors) > 0:
            self.validate_neighbors(sub_neighbors)

    def get_object_hash(self, id):
        """ Compute the hash with which the an object is tracked by the validator """
        return hashlib.sha1(id.encode('ascii')).hexdigest()

    def validate_object(self, object):
        """ Validate a single object """
        try:
            object_id = object.get_id()
        except GLib.Error as e:
            return

        if object_id == None:
            raise Error

        if self.get_object_hash(object_id) in self.seen:
            return

        self.seen.append(self.get_object_hash(object_id))

        try:
            validation_results = object.validate()
            for validation_result in validation_results:
                self.parse_validation_result(validation_result)
        except GLib.Error as e:
            pass

        if object is OParl.File:
            print("Found a file!")

        try:
            neighbors = object.get_neighbors()
            self.validate_neighbors(neighbors)
        except GLib.Error as e:
            print(e)
            exit()

    def get_schema_for_type(self, type):
        """ Get the schema for an entity """
        print(type)

    def cleanup_occured_excrement(self, client, excrement):
        """ Process the shit happened signal from liboparl """
        self.parse_validation_result(excrement)

    def parse_validation_result(self, validation_result):
        """ Parse a liboparl ValidationResult into a validator message """
        if self.get_object_hash(validation_result.get_object_id()) in self.seen:
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
