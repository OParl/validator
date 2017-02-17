# The MIT License (MIT)
#
# Copyright (c) 2017 Stefan Graupner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
from pathlib import Path
import requests
import hashlib
import datetime
import signal

import gi
gi.require_version('OParl', '0.2')

from gi.repository import OParl
from gi.repository import GLib

from src.cache import Cache
from src.result import Result

VALID_OPARL_VERSIONS = [
    "https://schema.oparl.org/1.0/"
]

def resolve_url(_, url):
    try:
        # TODO: get output of this into result log

        r = requests.get(url)
        r.raise_for_status()

        return r.text
    except Exception as e:
        return None


def catch_segfault(signum, frame):
    error_fatal_crash = """
Something went terribly wrong here. Please report this issue
at https://github.com/OParl/validator/issues/new.

To help us investigate, please try to rerun the validate command
as `validate -vvv <your_current_options_and_arguments>` and paste
the output of that command into the issue.

Thanks for your help,

the OParl Team
    """.strip()

    print(error_fatal_crash)
    raise OSError()


class Validator:
    url = ""
    schema_cache = {}
    client = None
    cache = None
    options = None
    result = None
    seen = []

    def __init__(self, url, options):
        signal.signal(signal.SIGSEGV, catch_segfault)

        self.url = url
        self.options = options

        self.client = OParl.Client()
        self.client.connect("resolve_url", resolve_url)

        self.result = Result()

        if options.redis:
            self.cache = Cache(url)

    def validate(self):
        self.result.debug("-- validation started --")

        system = self.client.open(self.url)
        self.validate_object(system)

        if self.options.validate_schema:
            version = system.get_oparl_version()

            msg = "Detected OParl Version {}"
            if version in VALID_OPARL_VERSIONS:
                self.result.ok(msg, version)
                self.check_schema_cache(version)
            else:
                self.result.error(msg + "\nExpected one of: {}", version, VALID_OPARL_VERSIONS)

        if self.options.save_results:
            with open('validation-log-{}.json'.format(str(datetime.datetime.now())[:19]), 'w') as f:
                f.write(json.dumps(self.result.messages))

        self.result.debug("-- validation completed --")

    def validate_neighbors(self, neighbors):
        sub_neighbors = []

        for neighbor in neighbors:
            try:
                self.validate_object(neighbor)
                sub_neighbors.extend(neighbor.get_neighbors())
            except GLib.Error as e:
                self.result.error("Failed to traverse object {}, error was: {}", type(neighbor), e)
                continue

        if len(sub_neighbors) > 0:
            self.validate_neighbors(sub_neighbors)

    def get_object_hash(self, object):
        return hashlib.sha1(object.get_id().encode('ascii')).hexdigest()

    def validate_object(self, object):
        try:
            object_id = object.get_id()
        except GLibError as e:
            self.result.error("Malformed object")
            return

        self.result.debug("In {}".format(object_id))

        if self.get_object_hash(object) in self.seen:
            self.result.debug("Revisiting {}".format(object_id))
            return

        self.result.debug("Appending to seen list")
        self.seen.append(self.get_object_hash(object))

        self.result.info("Validating {}", object_id)

        validation_result = []
        try:
            validation_result = object.validate()
        except GLib.Error as e:
            self.result.error("Object validation for '{}' failed".format(object_id))

        for validation_result in object.validate():
            severity = validation_result.get_severity()
            description = validation_result.get_description()

            if severity == OParl.ErrorSeverity.INFO:
                self.result.info(description)
            if severity == OParl.ErrorSeverity.WARNING:
                self.result.warning(description)
            if severity == OParl.ErrorSeverity.INFO:
                self.result.error(description)

#        if self.options.validate_schema:
#            # TODO: schema based validation
#            pass

        self.validate_neighbors(object.get_neighbors())

    def get_schema_for_type(self, type):
        # TODO: implement this once liboparl objects support get_type
        print(type)

    def check_schema_cache(self, schema_version):
        self.result.info("Building schema cache")
        schema_path = Path("schema_cache/{}".format(hashlib.sha1(schema_version.encode('ascii')).hexdigest()))
        schema_path.mkdir(parents=True, exist_ok=True)

        schema_listing = requests.get(schema_version).json()

        for schema in schema_listing:
            entity_path = schema_path / hashlib.sha1(schema.encode('ascii')).hexdigest()
            if entity_path.exists():
                with open(entity_path, 'r') as f:
                    self.schema_cache[schema] = json.loads(f.read())

            else:
                self.schema_cache[schema] = requests.get(schema).json()
                with open(entity_path, 'w') as f:
                    f.write(json.dumps(self.schema_cache[schema]))
