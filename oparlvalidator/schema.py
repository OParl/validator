# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from os.path import dirname, basename, join, splitext
import glob

SCHEMA_DIR = join(dirname(__file__), 'schema')

OPARL = dict()
for schema_file in glob.glob(join(SCHEMA_DIR, '*.json')):
    obj_type = splitext(basename(schema_file))[0]
    with open(schema_file, 'r') as schema:
        OPARL[obj_type] = json.load(schema)


# Additional validation functions here
def name_not_equal_shortName(data):
    """
    Validate that two values are not equal, e. g.
    name and nameShort may not be equal (section 5.2.3).
    """
    if 'name' not in data or 'nameShort' not in data:
        return True
    return not data['name'] == data['nameShort']
