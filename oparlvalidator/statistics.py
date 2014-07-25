# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
from functools import wraps
from collections import defaultdict


def with_stats(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs['stats'] = Statistics()
        func(*args, **kwargs)
    return wrapper


class Statistics(object):
    __shared_state = {}
    num_docs = 0
    num_docs_per_type = defaultdict(int)

    def __init__(self):
        # borg pattern
        self.__dict__ = self.__shared_state
        if 'initialized' not in self.__dict__:
            self.initialize()
            self.initialized = True

    def initialize(self):
        self.num_docs = 0

    def count_document(self):
        self.num_docs += 1

    def count_type(self, doc_type):
        self.num_docs_per_type[doc_type] += 1
