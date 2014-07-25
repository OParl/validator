# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from collections import namedtuple
from jsonschema.validators import Draft4Validator
from functools import wraps
import jsonschema.exceptions
from .schema import OPARL, TYPES
from .utils import build_object_type, import_from_string
from .statistics import with_stats


class ValidationNotice(namedtuple('ValidationNotice',
                       ['message', 'section'])):

    def __new__(cls, message, section=None):
        return super(ValidationNotice, cls).__new__(cls, message, section)


class ValidationError(namedtuple('ValidationError',
                      ['message', 'section'])):

    def __new__(cls, message, section=None):
        return super(ValidationError, cls).__new__(cls, message, section)


def prune(*args):
    def decorator(func):
        @wraps(func)
        def wrapper(*args_, **kwargs_):
            return (item for item in func(*args_, **kwargs_)
                    if item not in args)
        return wrapper
    return decorator


def types(*args):
    def decorator(func):
        func.types = args
        return func
    return decorator


def errormsg(msg):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if func(*args, **kwargs) is False:
                raise Exception(msg)
        return wrapper
    return decorator


class OParlResponse(object):

    def __init__(self, response):
        # TODO: doc me
        self.response = response
        self.validators = [name for name in dir(self)
                           if name.startswith('_validate_')]

    @types('AgendaItem', 'Document', 'Membership', 'Person',
           'Body', 'Location', 'Organization', 'System',
           'Consultation', 'Meeting', 'Paper')  # Or all by default?
    
    @errormsg("Invalid Status Code")
    def _validate_success(self):
        return self.response.status_code in range(200, 400)  # O(1) in Py 3

    @prune(None)
    def validate(self):
        # TODO: doc me
        if self.response:
            for name in self.validators:
                try:
                    getattr(self, name)()
                except Exception as error:
                    yield error


class OParlJson(object):

    def __init__(self, string):
        # TODO: doc me
        self.string = string

    @classmethod
    def _get_validator(cls, object_type):
        object_type = build_object_type(object_type)
        if object_type not in OPARL:
            return None
        return Draft4Validator(OPARL[object_type])

    @staticmethod
    def _validate_type(data):
        """
        Check if the document contains a type and we have a schema for it.

        :param data: dictionary with the parsed document for validation
        :returns: internal document type, could be used to access the
           approriate schema using the OPARL dictionary
        """
        type_check = {
            'type': 'object',
            'properties': {
                'type': {
                    'type': 'string',
                    'enum': TYPES.keys()
                }
            },
            'required': ['type']
        }
        Draft4Validator(type_check).validate(data)
        return TYPES[data['type']]

    @classmethod
    def _validate_schema(cls, obj_type, data):
        validator = cls._get_validator(obj_type)
        return validator.iter_errors(data)

    @classmethod
    def _validate_custom(cls, schema, data):
        if 'oparl:validate' in schema:
            for test in schema['oparl:validate']:
                func = import_from_string(test['method'])
                if not func(data):
                    yield ValidationError(section=test['section'],
                                          message=test['message'])

    @prune(None)
    @with_stats
    def validate(self, stats=None):
        # TODO: doc me
        try:
            data = json.loads(self.string)
            stats.count_document()
        except ValueError as excp:
            yield ValidationError('JSON error: %s' % excp)
            return
        try:
            obj_type = self._validate_type(data)
            stats.count_type(obj_type)
            # simple pass all errors to the caller
            for error in self._validate_schema(obj_type, data):
                yield error
            for error in self._validate_custom(OPARL[obj_type], data):
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
