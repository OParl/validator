# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import requests
from collections import defaultdict
from itertools import chain
from .validator import OParlJson, OParlResponse

EXPECTED_TYPES = {
    'hasMembership': ['oparl:Membership'],
}


def flattened(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, list):
            for item in value:
                yield key, item
        else:
            yield key, value


class Crawler(object):

    def __init__(self, seed_url, max_documents=None, type_whitelist=None,
                 recursive=True):
        # TODO: doc me
        self.seed_url = seed_url
        self.max_documents = max_documents
        self.type_whitelist = type_whitelist
        self.recursive = recursive
        self._counts = defaultdict(int)  # TODO: Depends on more schema data
        self._queue = [seed_url]
        self._valid = set()  # TODO: Persist
        self._invalid = set()
        self._errors = defaultdict(list)

    def _retrieve(self, *args, **kwargs):
        kwargs.setdefault('timeout', 10)
        return requests.get(*args, **kwargs)

    def _validate(self, response):
        # TODO: It should be configurable whether to raise an exception
        # or to collect all errors.
        return chain(OParlResponse(response).validate(),
                     OParlJson(response.text).validate())

    def run(self):
        # TODO: doc me
        while self._queue:
            url = self._queue.pop(0)
            response = self._retrieve(url)
            errors = list(self._validate(response))
            if not self.recursive:
                break
            dictionary = response.json()
            for key, types in EXPECTED_TYPES.items():
                if self.max_documents:
                    for type_ in types:
                        if self._counts[type_] >= self.max_documents:
                            continue
                values = dictionary.get(key)
                if isinstance(values, str):
                    values = [values]
                if values is not None:
                    for value in values:
                        if value in self._valid or value in self._invalid:
                            continue
                        # check for invalid URL params
                        self._queue.append(value)
                        for type_ in types:
                            self._counts[type_] += 1
            if len(errors) > 0:
                self._valid.add(url)
            else:
                self._invalid.add(url)
                self._errors[url].extend(errors)
        return self._valid
