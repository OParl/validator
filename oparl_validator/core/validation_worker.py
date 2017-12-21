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

from time import sleep
from threading import Thread

from oparl_validator.core.exceptions import ObjectValidationFailedException
from oparl_validator.core.output import Output
from oparl_validator.core.utils import get_entity_type_from_object


class ValidationWorker(Thread):
    def __init__(self, id, queue, seen_list, check_pool, result):
        super(ValidationWorker, self).__init__()
        self.check_pool = check_pool
        self.current_object = None
        self.id = id
        self.queue = queue
        self.result = result
        self.seen_list = seen_list

    def run(self):
        sleep(1)
        while not self.queue.empty():
            self.current_object = self.queue.get()

            if not self.is_seen_object():
                try:
                    results = self.validate_object()
                    self.save_validation_results(results)
                except ObjectValidationFailedException:
                    self.save_failed_object()

                Output.update_progress_bar('validation_progress', remaining=self.queue.qsize())
        Output.message('Quitting validation thread {}', self.id)

    def is_seen_object(self):
        if self.current_object.get_id() in self.seen_list:
            return True

        self.seen_list.push(self.current_object.get_id())

        return False

    def validate_object(self):
        validation_results = []

        try:
            validation_results = self.current_object.validate()
        except GLib.Error as glib_error:
            raise ObjectValidationFailedException from glib_error

        object_type = get_entity_type_from_object(self.current_object)
        extra_checks = self.check_pool.get_checks_for_type(object_type)

        for extra_check in extra_checks:
            extra_results = extra_check.evaluate(self.current_object)
            if extra_results is not None and type(extra_results) is 'list':
                 validation_results.extend(extra_results)

        return validation_results

    def save_validation_results(self, validation_results):
        self.result.acquire()

        if len(validation_results) > 0:
            self.result.failed_entities += 1

        for result in validation_results:
            self.result.parse_validation_result(self.current_object, result)

        self.result.release()

    def save_failed_object(self):
        self.result.acquire()
        self.result.fatal_objects.append(self.current_object)
        self.result.release()