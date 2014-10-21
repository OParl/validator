# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
from collections import defaultdict


num_docs = num_docs_per_type = properties = None


def initialize():
    global num_docs, num_docs_per_type, properties  # noqa
    num_docs = 0
    num_docs_per_type = defaultdict(int)
    properties = {
        'optional': defaultdict(lambda: defaultdict(int)),
        'recommended': defaultdict(lambda: defaultdict(int)),
        'custom': defaultdict(lambda: defaultdict(int))}
initialize()


def count_document():
    global num_docs  # noqa
    num_docs += 1


def count_type(doc_type):
    num_docs_per_type[doc_type] += 1


def _count_prop_helper(doc_type, doc_props, all_props, target, matching=True):
    for doc_prop in doc_props:
        if (doc_prop in all_props) == matching:
            target[doc_type][doc_prop] += 1


def count_properties(doc_type, doc_props, schema):
    all_props = schema['properties'].keys()
    if 'oparl:recommended' in schema:
        recommended_props = schema['oparl:recommended']
    else:
        recommended_props = []
    optional_props = [prop for prop in all_props
                      if prop not in schema['required']
                      and prop not in recommended_props]
    _count_prop_helper(doc_type, doc_props, all_props,
                       properties['custom'], False)
    _count_prop_helper(doc_type, doc_props, optional_props,
                       properties['optional'])
    _count_prop_helper(doc_type, doc_props, recommended_props,
                       properties['recommended'])


def message():
    output = '{} documents\n'.format(num_docs)
    for level, stats in properties.items():
        output += level.capitalize() + '\n'
        for url, obj in stats.items():
            output += '    {}: {} instances of {} properties\n'.format(
                url, sum(obj.values()), len(obj.values()))
    return output
