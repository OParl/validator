# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from jsonschema.validators import Draft4Validator
from .schema import OPARL


class OParlValidationError(Exception):
    def __init__(self, section, message):
        super(OParlValidationError, self).__init__()
        self.section = section
        self.message = message


class OParl(object):

    def __init__(self, string):
        self.string = string
        self.data = json.loads(string)
        self.links = []

    def _import_from_string(self, path):
        path_parts = path.split(':')
        if len(path_parts) < 2:
            raise ImportError("path must be in the form of "
                              "pkg.module.submodule:attribute")
        module = __import__(path_parts[0], fromlist=path_parts[1])
        return getattr(module, path_parts[1])

    def validate(self):
        type_check = {
            'type': 'object',
            'properties': {
                '@type': {
                    'type': 'string',
                    'enum': OPARL.keys()  # check if we have a schema for @type
                }
            }
        }
        Draft4Validator(type_check).validate(self.data)
        obj_type = self.data['@type']
        Draft4Validator(OPARL[obj_type]).validate(self.data)

        if 'oparl:validate' in OPARL[obj_type]:
            for test in OPARL[obj_type]['oparl:validate']:
                func = self._import_from_string(test['method'])
                if not func(self.data):
                    raise OParlValidationError(test['section'],
                                               test['message'])

        return True
