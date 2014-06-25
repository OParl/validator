# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from collections import namedtuple
from jsonschema.validators import Draft4Validator
import jsonschema.exceptions
from .schema import OPARL


class ValidationError(namedtuple('ValidationError', ['message', 'section'])):

    def __new__(cls, message, section=None):
        return super(ValidationError, cls).__new__(cls, message, section)


class OParl(object):

    def __init__(self, string=None, response=None):
        if string is response is None:
            raise ValueError('Specify either a JSON string or a response.')
        self.string = string
        self.response = response

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

    @staticmethod
    def _validate_type(data):
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
        Draft4Validator(type_check).validate(data)
        return data['@type']

    @classmethod
    def _validate_schema(cls, obj_type, data):
        validator = cls._get_validator(obj_type)
        return validator.iter_errors(data)

    @classmethod
    def _validate_custom(cls, obj_type, data):
        if 'oparl:validate' in OPARL[obj_type]:
            for test in OPARL[obj_type]['oparl:validate']:
                func = cls._import_from_string(test['method'])
                if not func(data):
                    yield ValidationError(section=test['section'],
                                          message=test['message'])

    def _validate_response_success(self):
        return self.response.status_code in range(200, 400)  # O(1) in Py 3

    def validate(self):
        if self.response:
            for name in dir(self):
                if name.startswith('_validate_response_'):
                    if not getattr(self, name)():
                        yield ValidationError('URL invalid')
                        return
                    else:
                        self.string = self.response.text

        if not self.string:
            yield ValidationError('No data for validation')
            return

        try:
            data = json.loads(self.string)
        except ValueError as excp:
            yield ValidationError('JSON error: %s' % excp)
            return

        try:
            obj_type = self._validate_type(data)

            # simple pass all errors to the caller
            for error in self._validate_schema(obj_type, data):
                yield error
            for error in self._validate_custom(obj_type, data):
                yield error

        except (jsonschema.exceptions.ValidationError,
                jsonschema.exceptions.SchemaError) as excp:
            # _validate_type may raise an exception, we translate it
            # here into en apropriate ValidationError and pass it to
            # the caller (if the type does not validate, it does not
            # make sense to continue validation
            if len(excp.path) > 0:
                yield ValidationError('"{}": {}'.format(''.join(excp.path),
                                                        excp.message))
            else:
                yield ValidationError(excp.message)
