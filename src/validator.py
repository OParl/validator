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
import redis
import hashlib

import gi
gi.require_version('OParl', '0.2')

from gi.repository import OParl

from src.cache import Cache
from src.result import Result

VALID_OPARL_VERSIONS = [
    "https://schema.oparl.org/1.0/"
]

class Validator:
    url = ""
    client = None
    cache = None
    options = None

    def __init__(self, url, options):
        self.url = url
        self.options = options

        self.client = OParl.Client()
        self.client.connect("resolve_url", Validator.resolve_url)

        if options.redis:
            self.cache = Cache(url)

    def resolve_url(_, url):
        try:
            r = requests.get(url)
            r.raise_for_status()

            return r.text
        except Exception as e:
            return None

    def validate(self):
        result = Result()

        result.info("Validating \"{}\"", self.url)

        system = self.client.open(self.url)
        version = system.get_oparl_version()

        # map<EntityName,JSONSchema>
        schema = None

        msg = "Detected OParl Version {}"
        if (version in VALID_OPARL_VERSIONS):
            result.ok(msg, version)
            schema = self.check_schema_cache(version)
        else:
            result.error(msg + "\nExpected one of: {}", version, VALID_OPARL_VERSIONS)

    def check_schema_cache(self, schema_version):
        schema_path = Path("schema_cache/{}".format(hashlib.sha1(schema_version.encode('ascii')).hexdigest()))
        schema_path.mkdir(parents=True, exist_ok=True)

        schema_cache = {}

        schema_listing = requests.get(schema_version).json()
        for schema in schema_listing:
            entity_path = schema_path / hashlib.sha1(schema.encode('ascii')).hexdigest()
            if entity_path.exists():
                with open(entity_path, 'r') as f:
                    loaded_json = json.loads(f.read())
                    schema_cache[schema] = loaded_json

            else:
                schema_json = requests.get(schema).json()
                schema_cache[schema] = schema_json
                with open(entity_path, 'w') as f:
                    f.write(json.dumps(schema_json))

        return schema_cache
