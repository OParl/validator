# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
import requests
import jsonschema.exceptions
from collections import namedtuple
from jsonschema.validators import Draft4Validator
from functools import wraps
from itertools import chain, groupby
from operator import itemgetter
from six.moves import zip  # pylint: disable=redefined-builtin,import-error
from .schema import OPARL, TYPES
from .utils import import_from_string
from .statistics import with_stats


class ValidationError(namedtuple('ValidationError',
                                 ['message', 'section'])):
    """Class to capture validation errors."""

    def __new__(cls, message, section=None):
        return super(ValidationError, cls).__new__(cls, message, section)


def prune(*args):
    """Removes values equivalent to the passed parameters from the result of
    a function that returns an iterable."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args_, **kwargs_):
            return (item for item in func(*args_, **kwargs_)
                    if item not in args)
        return wrapper
    return decorator


def types(*args):
    """Annotates a function with the types it is meant to validate. We
    can use the empty case as a wildcard.

    The implicity can easily be thwarted in a containing class, and the
    alternative would not be as DRY since our function names are more
    likely to change than OParl’s object names once the standard has been
    released. But I don’t have a strong preference either way.
    """
    def decorator(func):
        func.types = args
        return func
    return decorator


def validation_error(*args, **kwargs):
    """Converts a boolean return value to a custom ValidationError."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args_, **kwargs_):
            if func(*args_, **kwargs_) is False:
                yield ValidationError(*args, **kwargs)
        return wrapper
    return decorator


class OParlResponse(object):
    """Validator for server responses."""

    def __init__(self, response):
        """Initializes the validator with the candidate response."""
        self.response = response
        self.validators = [method
                           for name, method
                           in sorted(self.__class__.__dict__.items())
                           if name.startswith('_validate_')]

    @types()
    @validation_error('Invalid Status Code')
    def _validate_success(self):
        """Validates the HTTP status code."""
        return self.response.status_code in range(200, 400)  # O(1) in Py 3

    def validate(self):
        """Executes all applicable response validators."""
        return chain.from_iterable([val(self) for val in self.validators])


class OParlJson(object):
    """Validator for OParl objects."""

    def __init__(self, string):
        """Initializes the validator with a string that consists of the
        JSON object."""
        self.string = string

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
    def _validate_schema(schema, data):
        """Runs the JSON Schema validation."""
        validator = Draft4Validator(schema)
        return validator.iter_errors(data)

    @staticmethod
    def _validate_custom(schema, data):
        """Executes all custom validators for the object."""
        if 'oparl:validate' in schema:
            for test in schema['oparl:validate']:
                func = import_from_string(test['method'])
                if not func(data):
                    yield ValidationError(section=test['section'],
                                          message=test['message'])

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
        schema = OPARL[obj_type]

        return chain(cls._validate_schema(schema, data),
                     cls._validate_custom(schema, data))

    def validate(self):
        """Runs the validation and yields any validation errors."""
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


class ServerSuite(object):

    def __init__(self, links, limit=3):
        """Initializes the suite with a corpus of valid URLs."""
        self.links = {type_: list(next(zip(*links_)))[:limit]
                      for type_, links_
                      in groupby(sorted(links, key=itemgetter(1)),
                                 key=itemgetter(1))}
        self.validators = [method for name, method
                           in sorted(self.__class__.__dict__.items())
                           if name.startswith('_validate_')]

    def validate(self):
        for valitator in self.validators:
            yield valitator()

    @types('http://oparl.org/schema/1.0/File')
    @validation_error('HEAD response invalid', section='4.8.1')
    def _validate_head_for_file_urls(self, url):
        """Section 4.8.1 requires that file URLs have to allow for HEAD
        requests.
        """
        object_ = requests.get(url, timeout=10).json()
        response = requests.head(
            object_.get('downloadUrl', object_['accessUrl']), timeout=10)
        return response.status_code in range(200, 400)

    @types('http://oparl.org/schema/1.0/File')
    @validation_error('Content-Disposition missing or incomplete',
                      section='4.8.2')
    def _validate_filename_for_file_urls(self, url):
        """Section 4.8.2 requires that the server specify the name of a file
        in a Content-Disposition header if it has a download URL.
        """
        object_ = requests.get(url, timeout=10).json()
        if 'downloadUrl' in object_:
            response = requests.head(object_['downloadUrl'], timeout=10)
            cd_header = response.headers.get('Content-Disposition', ''),
            return 'attachment' in cd_header and 'filename' in cd_header

    @types('http://oparl.org/schema/1.0/File')
    @validation_error('Last-Modified header missing', section='4.8.3')
    def _validate_last_modified_for_file_urls(self, url):
        """Section 4.8.3 requires that access and download URLs have to
        provide Last-Modified headers.
        """
        object_ = requests.get(url, timeout=10).json()
        if 'downloadUrl' in object_:
            response = requests.head(object_['downloadUrl'], timeout=10)
            if 'Last-Modified' not in response.headers:
                return False
        response = requests.head(object_['accessUrl'], timeout=10)
        return 'Last-Modified' in response.headers
