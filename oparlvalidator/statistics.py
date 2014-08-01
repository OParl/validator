# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
from functools import wraps
from collections import defaultdict


def with_stats(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs['stats'] = Statistics()
        return func(*args, **kwargs)
    return wrapper


class Statistics(object):
    __shared_state = {}
    num_docs = 0
    num_docs_per_type = defaultdict(int)
    properties = {
        'optional': defaultdict(lambda: defaultdict(int)),
        'recommended': defaultdict(lambda: defaultdict(int)),
        'custom': defaultdict(lambda: defaultdict(int))
    }

    def __init__(self):
        # borg pattern
        self.__dict__ = self.__shared_state
        if 'initialized' not in self.__dict__:
            self.initialize()
            self.initialized = True

    def initialize(self):
        self.num_docs = 0
        self.num_docs_per_type = defaultdict(int)
        self.properties = {
            'optional': defaultdict(lambda: defaultdict(int)),
            'recommended': defaultdict(lambda: defaultdict(int)),
            'custom': defaultdict(lambda: defaultdict(int))
        }

    def count_document(self):
        self.num_docs += 1

    def count_type(self, doc_type):
        self.num_docs_per_type[doc_type] += 1

    def _count_prop_helper(self, doc_type, doc_props, all_props,
                           target, matching=True):
        for doc_prop in doc_props:
            if (doc_prop in all_props) == matching:
                target[doc_type][doc_prop] += 1

    def count_properties(self, doc_type, properties, schema):
        all_props = schema['properties'].keys()

        if 'oparl:recommended' in schema:
            recommended_props = schema['oparl:recommended']
        else:
            recommended_props = list()

        optional_props = [prop for prop in all_props
                          if prop not in schema['required']
                          and prop not in recommended_props]

        self._count_prop_helper(doc_type, properties, all_props,
                                self.properties['custom'], False)
        self._count_prop_helper(doc_type, properties, optional_props,
                                self.properties['optional'])
        self._count_prop_helper(doc_type, properties, recommended_props,
                                self.properties['recommended'])
