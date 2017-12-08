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
from datetime import datetime, timedelta
from subprocess import check_output
from threading import Lock

from beautifultable import BeautifulTable
import gi

from core.utils import get_entity_type_from_object
from core.utils import sha1_hexdigest

summary_template = """
Totals:
\t{} Entities
\t{} valid
\t{} failed
\t{} fatal
"""

network_template = """
Network:
\t{}
\tAverage response time: {}
"""

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

    def __init__(self, compiled_result = None):
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
        self.lock = Lock()

        self.compiled_result = compiled_result

    def format_severity(self, severity):
        if type(severity) is 'string':
            return severity

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

    def compile(self):
        timestamp = datetime.now().isoformat()

        self.compiled_result = {
            'counts': {
                'total': self.total_entities,
                'valid': self.total_entities - self.failed_entities,
                'failed': self.failed_entities,
                'fatal': len(self.fatal_objects)
            },
            'object_messages': self.object_messages,
            'network': self.network,
            'oparl_version': self.oparl_version,
            'timestamp': timestamp
        }

    def __str__(self):
        return self.text()

    def text(self):
        totals = summary_template.format(
            self.compiled_result['counts']['total'],
            self.compiled_result['counts']['valid'],
            self.compiled_result['counts']['failed'],
            self.compiled_result['counts']['fatal']
        )

        ssl_info = 'No valid SSL certificate detected'
        if self.compiled_result['network']['ssl']:
            ssl_info = 'Valid SSL certificate detected'

        network = network_template.format(
            ssl_info,
            self.compiled_result['network']['average_ttl']
        )

        try:
            max_columns = int(subprocess.check_output(['stty', 'size']).split()[1])
        except Exception:
            max_columns = 80

        entities = ''

        for entity, messages in self.compiled_result['object_messages'].items():
            table = BeautifulTable(max_columns)
            table.column_headers = ['', 'severity', 'message', 'occurences']

            entity_list = ''

            message_key = 1
            for message in messages:
                message = self.compiled_result['object_messages'][entity][message]

                row = []

                row.append(message_key)
                row.append(message['severity'])
                row.append(message['message'])
                row.append(message['count'])

                for object in message['objects']:
                    entity_list += '[{}] {},\n'.format(message_key, object)

                table.append_row(row)
                message_key += 1

            entities += '# {}\n{}\n\nAffected Entities:\n\n{}\n\n'.format(entity, table, entity_list[:-2])

        return 'Validation Result:\n\n{}\n{}\n{}\n'.format(totals, network, entities[:-2])

    def json(self):
        class DateTimeEncoder(json.JSONEncoder):
            """ Fixup for timedelta not being json serializable. https://stackoverflow.com/a/27058505/3549270 """

            def default(self, o):
                if isinstance(o, timedelta):
                    return o.total_seconds()

                return json.JSONEncoder.default(self, o)

        try:
            return json.dumps(self.compiled_result, cls=DateTimeEncoder)

        except KeyError as e:
            Output.exception(e)

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()

    @staticmethod
    def from_file(file_name):
        with open(file_name, 'r') as f:
            compiled_result = json.load(f)
            result = Result(compiled_result=compiled_result)
            return result
