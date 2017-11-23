"""
The MIT License (MIT)

Copyright (c) 2017 Stefan Graupner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from datetime import datetime

import gi

from .utils import get_entity_type_from_object
from .utils import sha1_hexdigest

gi.require_version('OParl', '0.2')

from gi.repository.OParl import ErrorSeverity


class Result:
    """
    Validation Result

    The validation result contains a set of messages for each object
    type as well as some general statistics and messages regarding
    validation events that do not belong into the above categories.
    That last category, among other things, keeps taps on what objects
    or files were unreachable.
    """

    def __init__(self, cache):
        self.total_entities = 0
        self.failed_entities = 0

        self.object_messages = {}

        # this is a list of objects that lead to unrecoverable error in respect to the spec
        self.fatal_objects = []

        self.network = {
            'average_ttl': 0,
            'ssl': False,
            'encodings': []
        }

        self.oparl_version = '1.0'
        self.cache = cache

    def format_severity(self, severity):
        # TODO: Rewrite this to handle ValidationResult Severities?
        mapping = {
            ErrorSeverity.ERROR: 'error',
            ErrorSeverity.WARNING: 'warning',
            ErrorSeverity.INFO: 'info',
        }
        return mapping[severity]

    def parse_validation_result(self, object, validation_result):
        """ Parses a liboparl ValidationResult into a validator message. """
        severity = validation_result.get_severity()
        description = validation_result.get_description()

        entity_type = get_entity_type_from_object(object)

        if entity_type not in self.object_messages:
            self.object_messages[entity_type] = {}

        new_message = {
            'severity': self.format_severity(severity),
            'message': description,
            'count': 0,
            'objects': []
        }

        message_hash = sha1_hexdigest(entity_type + description)

        # insert message dict
        if message_hash not in self.object_messages[entity_type]:
            self.object_messages[entity_type][message_hash] = new_message

        # increment message occurence counter and add object id to reference list
        message = self.object_messages[entity_type][message_hash]

        message['count'] += 1
        if object.get_id() not in message['objects']:
            message['objects'].append(object.get_id())

        self.object_messages[entity_type][message_hash] = message

    def compiled_result(self):
        timestamp = datetime.now().isoformat()

        return {
            'counts': {
                'total': self.total_entities,
                'valid': self.total_entities - self.failed_entities,
                'failed': self.failed_entities,
                'fatal': len(self.fatal_objects)
            },
            'object_messages': self.object_messages,
            #'network': self.network,
            'oparl_version': self.oparl_version,
            'timestamp': timestamp
        }

    def __str__(self):
        return self.text()

    def text(self):
        from beautifultable import beautifultable

        result = self.compiled_result()

        totals = 'Totals:\n' \
            + '{} Entities,\n' \
            + '\t{} valid\n', \
            + '\t{} failed\n', \
            + '\t{} fatal'.format(
                result['counts']['total'],
                result['counts']['valid'],
                result['counts']['failed'],
                result['counts']['fatal']
            )

        entities = ''

        for entity in result['object_messages']:
            entites += ''.format(entity)

        return 'Validation Result:\n\n' + totals

    def json(self):
        try:
            return json.dumps(self.compiled_result())
        except KeyError as e:
            print(e)
