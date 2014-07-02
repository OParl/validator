# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from os.path import dirname, basename, join, splitext
import glob
from functools import partial

from .utils import LazyDict

SCHEMA_DIR = join(dirname(__file__), 'schema')


def _load_schema(filename):
    with open(filename, 'r') as schema:
        return json.load(schema)


OPARL = LazyDict()
for schema_file in glob.glob(join(SCHEMA_DIR, '*.json')):
    obj_type = splitext(basename(schema_file))[0]
    OPARL[obj_type] = partial(_load_schema, schema_file)


# Additional validation functions here
def nameLong_not_equal_nameShort(data):
    """
    Validate that two values are not equal, e. g.
    nameLong and nameShort may not be equal (section 5.2.3).
    """
    if 'nameLong' not in data or 'nameShort' not in data:
        return True
    return not data['nameLong'] == data['nameShort']
