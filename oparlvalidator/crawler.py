# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import requests
from collections import defaultdict
from itertools import chain
from .schema import EXPECTED_TYPES
from .validator import OParlJson, OParlResponse


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
        self._counts = defaultdict(int)
        self._queue = [(seed_url, [])]
        self._valid = set()  # TODO: Persist?
        self._invalid = set()
        self._errors = defaultdict(list)

    def _retrieve(self, *args, **kwargs):
        kwargs.setdefault('timeout', 10)
        return requests.get(*args, **kwargs)

    def _validate(self, response):
        return chain(OParlResponse(response).validate(),
                     OParlJson(response.text).validate())

    def _mine(self, document):
        if 'type' not in document:
            # this document is not valid, we cannot detect its type, so we
            # do not know what items should contain links to other documents
            return

        for key, value in document.items():
            expected_types = EXPECTED_TYPES[document['type']].get(key)
            if expected_types:
                if isinstance(value, str):
                    yield (value, expected_types)
                else:
                    for item in value:
                        yield (item, expected_types)

    def run(self):
        # TODO: doc me
        while self._queue:
            url, expected_types = self._queue.pop(0)
            response = self._retrieve(url)
            errors = list(self._validate(response))
            if errors:
                self._invalid.add(url)
                self._errors[url].extend(errors)
            else:
                self._valid.add(url)
            if not self.recursive:
                return self._errors
            # Queuing new URLs
            links = self._mine(response.json())
            for url, expected_types in links:
                # Skip because of limits per type
                if self.max_documents is not None:
                    if len(expected_types) == 1:
                        if self._counts[expected_types[0]] >= \
                                self.max_documents:
                            continue
                    else:  # TODO: Decide how to handle the ambiguous cases
                        continue
                # Skip because known
                if url in self._valid or url in self._invalid:
                    continue
                self._queue.append((url, expected_types))
                self._counts[expected_types[0]] += 1
        return self._errors
