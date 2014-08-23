# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import requests
from collections import defaultdict, namedtuple
from itertools import chain
from .schema import EXPECTED_TYPES
from .validator import OParlJson, OParlResponse, ServerSuite
import six


class DocumentSpec(namedtuple('DocumentSpec',
                              ['url', 'expected_types', 'parent'])):
    def __new__(cls, url, expected_types=None, parent=None):
        return super(DocumentSpec, cls).__new__(cls, url, expected_types,
                                                parent)


LinkSource = namedtuple('LinkSource', ['url', 'key'])


class Crawler(object):
    """A tool for crawling an OParl server."""

    def __init__(self, seed_url, max_documents=None, type_whitelist=(),
                 recursive=True):
        """Initilizes the crawler with a seed URL that serves as entry point
        for the crawling process, an optional limit on the number of documents
        per type that need to be tested, an optional whitelist of types, and
        the option of deactivating recursion.
        """
        self.seed_url = seed_url
        self.max_documents = max_documents
        self.type_whitelist = set(type_whitelist)
        self.recursive = recursive
        self._counts = defaultdict(int)
        self._queue = [DocumentSpec(url=seed_url)]
        self._visited = set()
        self._valid = set()  # TODO: Persist?
        self._errors = defaultdict(list)

    def _retrieve(self, *args, **kwargs):
        """Performs the actual retrieval, whereby the parameters are the ones
        of the requests.get method."""
        kwargs.setdefault('timeout', 10)
        return requests.get(*args, **kwargs)

    def _validate(self, response, doc):
        """Calls the validators."""
        return chain(OParlResponse(response).validate(),
                     OParlJson(response.text).validate(doc))

    def _mine(self, document, parent):
        """Mines the response for URLs that can be followed."""
        if not ('type' in document and document['type'] in EXPECTED_TYPES):
            # We cannot detect the type of this document, so we do not know
            # what parameters should contain links to other documents.
            return
        for key, value in document.items():
            expected_types = EXPECTED_TYPES[document['type']].get(key)
            if expected_types:
                if isinstance(value, six.string_types):
                    yield DocumentSpec(value, expected_types=expected_types,
                                       parent=LinkSource(parent.url, key))
                else:
                    for item in value:
                        yield DocumentSpec(item, expected_types=expected_types,
                                           parent=LinkSource(parent.url, key))

    def run(self):
        """Starts the crawling process."""
        # TODO: List handling
        while self._queue:
            doc = self._queue.pop(0)
            response = self._retrieve(doc.url)
            self._visited.add(doc.url)
            error = None
            for error in self._validate(response, doc):
                self._errors[doc.url].append(error)
                yield (doc.url, error)
            object_ = response.json()
            if not error:
                self._valid.add((doc.url, object_['type']))
            if not self.recursive:
                return

            # Queuing new URLs
            for new_doc in self._mine(object_, doc):
                if self.type_whitelist:
                    if not set(new_doc.expected_types) & self.type_whitelist:
                        continue
                # Skip because of limits per type
                if self.max_documents is not None:
                    if len(new_doc.expected_types) == 1:
                        if self._counts[new_doc.expected_types[0]] >= \
                                self.max_documents:
                            continue
                        self._counts[new_doc.expected_types[0]] += 1
                    else:  # TODO: Decide how to handle the ambiguous cases
                        continue
                # Skip because known
                if new_doc.url in self._visited:
                    continue
                self._queue.append(new_doc)
        ServerSuite(self._valid).validate()
