# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from collections import namedtuple
from jsonschema.validators import Draft4Validator
from functools import wraps
from itertools import chain
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


def validation_error(*args, **kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(*args_, **kwargs_):
            if func(*args_, **kwargs_) is False:
                yield ValidationError(*args, **kwargs)
        return wrapper
    return decorator


class OParlResponse(object):

    def __init__(self, response):
        # TODO: doc me
        self.response = response
        self.validators = [method
                           for name, method
                           in sorted(self.__class__.__dict__.items())
                           if name.startswith('_validate_')]

    @types('AgendaItem', 'Document', 'Membership', 'Person',
           'Body', 'Location', 'Organization', 'System',
           'Consultation', 'Meeting', 'Paper')  # Or all by default?
    @validation_error("Invalid Status Code")
    def _validate_success(self):
        return self.response.status_code in range(200, 400)  # O(1) in Py 3

    def validate(self):
        return chain.from_iterable([val(self) for val in self.validators])


class OParlJson(object):

    def __init__(self, string):
        # TODO: doc me
        self.string = string

    @staticmethod
    def _get_validator(object_type):
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

    @staticmethod
    def _validate_custom(schema, data):
        if 'oparl:validate' in schema:
            for test in schema['oparl:validate']:
                func = import_from_string(test['method'])
                if not func(data):
                    yield ValidationError(section=test['section'],
                                          message=test['message'])

    @classmethod
    def _validate_schema(cls, obj_type, data):
        validator = cls._get_validator(obj_type)
        return validator.iter_errors(data)

    @staticmethod
    @with_stats
    def _load_document(content, stats=None):
        data = json.loads(content)
        stats.count_document()
        return data

    @classmethod
    @prune(None)
    @with_stats
    def _validate_all(cls, data, stats=None):
        obj_type = cls._validate_type(data)
        stats.count_type(obj_type)

        return chain(cls._validate_schema(obj_type, data),
                     cls._validate_custom(OPARL[obj_type], data))

    def validate(self):
        # TODO: doc me
        try:
            document = self._load_document(self.string)
            for error in self._validate_all(document):
                yield error
        except (jsonschema.exceptions.ValidationError,
                jsonschema.exceptions.SchemaError,
                ValueError) as excp:
            # _load_document or _validate_all may raise an exception,
            # we translate it here into en apropriate ValidationError
            # and pass it to the caller (if the type does not validate,
            # it does not make sense to continue validation
            if hasattr(excp, 'path') and len(excp.path) > 0:
                yield ValidationError('"{}": {}'.format(''.join(excp.path),
                                                        excp))
            else:
                yield ValidationError(excp)
