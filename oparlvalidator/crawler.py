# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import requests
from collections import defaultdict
from itertools import chain
from .schema import EXPECTED_TYPES
from .validator import OParlJson, OParlResponse


class Crawler(object):
    """A tool for crawling an OParl server."""

    def __init__(self, seed_url, max_documents=None, type_whitelist=None,
                 recursive=True):
        """Initilizes the crawler with a seed URL that serves as entry point
        for the crawling process, an optional limit on the number of documents
        per type that need to be tested, an optional whitelist of types, and
        the option of deactivating recursion.
        """
        self.seed_url = seed_url
        self.max_documents = max_documents
        self.type_whitelist = type_whitelist
        self.recursive = recursive
        self._counts = defaultdict(int)
        self._queue = [(seed_url, [])]
        self._visited = set()  # TODO: Persist?
        self._errors = defaultdict(list)

    def _retrieve(self, *args, **kwargs):
        """Performs the actual retrieval, whereby the parameters are the ones
        of the requests.get method."""
        kwargs.setdefault('timeout', 10)
        return requests.get(*args, **kwargs)

    def _validate(self, response):
        """Calls the validators."""
        return chain(OParlResponse(response).validate(),
                     OParlJson(response.text).validate())

    def _mine(self, document):
        """Mines the response for URLs that can be followed."""
        if not ('type' in document and document['type'] in EXPECTED_TYPES):
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
        """Starts the crawling process."""
        while self._queue:
            url, expected_types = self._queue.pop(0)
            response = self._retrieve(url)
            self._visited.add(url)

            for error in self._validate(response):
                self._errors[url].append(error)
                yield (url, error)

            if not self.recursive:
                return

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
                if url in self._visited:
                    continue
                self._queue.append((url, expected_types))
                self._counts[expected_types[0]] += 1
