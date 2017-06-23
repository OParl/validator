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

from colorama import Fore, Style

from gi.repository import OParl
from gi.repository.OParl import ErrorSeverity

from src.utils import *
from src.cache import *


class Result(object):
    """
        Validation Result

        The validation result contains a set of messages for each object
        type as well as some general statistics and messages regarding
        validation events that do not belong into the above categories.
        That last category, among other things, keeps taps on what objects
        or files were unreachable.
    """

    total_entities = 0
    failed_entities = 0

    object_messages = {}

    """ this is a list of objects that lead to unrecoverable error in respect to the spec """
    fatal_objects = []

    network = {
        'average_ttl': 0,
        'ssl': False,
        'encodings': []
    }

    oparl_version = '1.0'

    cache = None

    def __init__(self, cache):
        self.cache = cache

    def format_severity(self, severity):
        # TODO: Rewrite this to handle ValidationResult Severities?
        if severity == ErrorSeverity.ERROR:
            return 'error'
        if severity == ErrorSeverity.WARNING:
            return 'warning'
        if severity == ErrorSeverity.INFO:
            return 'info'

    def parse_validation_result(self, object, validation_result):
        """
            Parse a liboparl ValidationResult into a validator message
        """
        severity = validation_result.get_severity()
        description = validation_result.get_description()

        oparl_type = OParlType(object)

        if oparl_type.entity not in self.object_messages:
            self.object_messages[oparl_type.entity] = {}

        new_message = {
            'severity': self.format_severity(severity),
            'message': description,
            'count': 0,
            'objects': []
        }

        message_hash = sha1_hexdigest(oparl_type.entity + description)

        # insert message dict
        if message_hash not in self.object_messages[oparl_type.entity]:
            self.object_messages[oparl_type.entity][message_hash] = new_message

        # increment message occurence counter and add object id to reference list
        message = self.object_messages[oparl_type.entity][message_hash]

        message['count'] += 1
        if object.get_id() not in message['objects']:
            message['objects'].append(object.get_id())

        self.object_messages[oparl_type.entity][message_hash] = message

    def compiled_result(self):
        return {
            'counts': {
                'total': self.total_entities,
                'valid': self.total_entities - self.failed_entities,
                'failed': self.failed_entities,
                'fatal': len(self.fatal_objects)
            },
            'object_messages': self.object_messages,
            'network': self.network,
            'oparl_version': self.oparl_version,
            'timestamp': datetime.now().isoformat()
        }

    def __str__(self):
        return json.dumps(self.compiled_result())
