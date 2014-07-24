# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from os.path import join
import glob

from .utils import LazyDict, build_object_type, SCHEMA_DIR


def _schema_loader(filename):
    def load():
        with open(filename, 'r') as schema:
            return json.load(schema)
    return load


def _build_schema_url(objtype):  # TODO: Can we make this the default?
    return 'http://oparl.org/' + objtype


def _find_expected_types(schema):
    return {_build_schema_url(parent_type): {
                key: [_build_schema_url(type_)  # noqa
                      for type_ in desc['oparl:linksTo']]
                for key, desc in parent['properties'].items()
                if 'oparl:linksTo' in desc}
            for parent_type, parent in schema.items()}


OPARL = LazyDict()
for schema_file in glob.glob(join(SCHEMA_DIR, '*', '*.json')):
    obj_type = build_object_type(schema_file)
    OPARL[obj_type] = _schema_loader(schema_file)
TYPES = {_build_schema_url(obj): obj for obj in OPARL.keys()}
EXPECTED_TYPES = _find_expected_types(OPARL)


# Additional validation functions here
def nameLong_not_equal_nameShort(data):
    """
    Validate that two values are not equal, e. g.
    nameLong and nameShort may not be equal (section 5.2.3).
    """
    if 'nameLong' not in data or 'nameShort' not in data:
        return True
    return not data['nameLong'] == data['nameShort']
