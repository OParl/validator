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

    def __init__(self, string=None, response=None):
        if string is response is None:
            raise ValueError('Specify either a JSON string or a response.')
        self.string = string
        self.response = response
        self.data = None

    @staticmethod
    def _import_from_string(path):
        path_parts = path.split(':')
        if len(path_parts) != 2:
            raise ImportError('path must be in the form of '
                              'pkg.module.submodule:attribute')
        module = __import__(path_parts[0], fromlist=path_parts[1])
        return getattr(module, path_parts[1])

    @staticmethod
    def _build_object_type(object_type):
        if object_type.startswith('oparl:'):
            return object_type
        parts = object_type.split('_')
        return 'oparl:%s' % ''.join([part.capitalize() for part in parts])

    @classmethod
    def _get_validator(cls, object_type):
        object_type = cls._build_object_type(object_type)
        if object_type not in OPARL:
            return None
        return Draft4Validator(OPARL[object_type])

    def _validate_type(self):
        type_check = {
            'type': 'object',
            'properties': {
                '@type': {
                    'type': 'string',
                    'enum': OPARL.keys()  # check if we have a schema for @type
                }
            },
            'required': ['@type']
        }
        Draft4Validator(type_check).validate(self.data)
        return self.data['@type']

    def _validate_schema(self, obj_type, data):
        validator = self._get_validator(obj_type)
        validator.validate(data)

    def _validate_custom(self, obj_type, data):
        if 'oparl:validate' in OPARL[obj_type]:
            for test in OPARL[obj_type]['oparl:validate']:
                func = self._import_from_string(test['method'])
                if not func(data):
                    raise OParlValidationError(test['section'],
                                               test['message'])

    def _validate_response_success(self):
        if self.response.status_code not in range(200, 400):  # O(1) in Py 3
            raise OParlValidationError(None, 'URL invalid')

    def validate(self):
        if self.response:
            for name in dir(self):
                if name.startswith('_validate_response_'):
                    getattr(self, name)()
            self.string = self.response.text
        self.data = json.loads(self.string)
        obj_type = self._validate_type()
        self._validate_schema(obj_type, self.data)
        self._validate_custom(obj_type, self.data)
        return True
