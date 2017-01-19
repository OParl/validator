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

import requests
import json
import redis

from colorama import Fore, Style

import gi
gi.require_version('OParl', '0.2')

from gi.repository import OParl

from src.cache import Cache;

VALID_OPARL_VERSIONS = [
    "https://schema.oparl.org/1.0"
]

class Validator:
    url = ""
    client = None
    cache = None

    def __init__(self, url, redis=True):
        self.url = url

        self.client = OParl.Client()
        self.client.connect("resolve_url", Validator.resolve_url)

        if redis:
            self.cache = Cache(url)

        self.validate()

    def resolve_url(_, url):
        try:
            r = requests.get(url)
            r.raise_for_status()

            return r.text
        except Exception as e:
            return None

    def info(self, message, *args):
        # TODO: make this output controllable
        print(message.format(*args))

    def ok(self, message, *args):
        # TODO: make this output controllable
        message = message.format(*args)
        print("{}[OK] {}{}".format(Fore.GREEN, message, Style.RESET_ALL))

    def error(self, message, *args):
        # TODO: make this output controllable
        message = message.format(*args)
        print("{}[ERR] {}{}".format(Fore.RED, message, Style.RESET_ALL))

    def validate(self):
        self.info("Validating \"{}\"", self.url)
        system = self.client.open(self.url)
        version = system.get_oparl_version()

        msg = "Detected OParl Version {}"
        if (version in VALID_OPARL_VERSIONS):
            self.ok(msg, version)
        else:
            self.error(msg + "\nExpected one of: {}", version, VALID_OPARL_VERSIONS)
