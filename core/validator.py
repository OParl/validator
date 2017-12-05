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

import sys
from threading import activeCount, Thread
from time import sleep

from core.client import Client
from core.entity_queue import EntityQueue
from core.exceptions import \
    EndpointNotReachableException, \
    EndpointIsNotAnOParlEndpointException, \
    ObjectValidationFailedException
from core.output import Output
from core.result import Result
from core.seen_list import SeenList

VALID_OPARL_VERSIONS = [
    "https://schema.oparl.org/1.0/"
]

class Validator:
    """
        This class provides a Validator instance.

        The OParl Validator always requires an endpoint to validate
        and an optional set of options which, if given, should
        be an argparse.Namespace object.

        Please refer to `self.parse_options` for a listing of
        currently available options.

        In order to run, the Validator requires a redis connection
        which currently must be on the same machine.
    """

    NUM_VALIDATION_WORKERS = 3
    ENTITY_QUEUE_SIZE = 10

    def __init__(self, endpoint, options = None):
        self.endpoint = endpoint
        self.options = self.parse_options(options)

        Output.initialize(
            self.options.porcelain,
            self.options.silent,
            self.options.verbosity
        )

        if self.options.porcelain and self.options.result is None:
            Output.message('You selected an invalid option, please provide a result destination filename')
            exit(1)

    def parse_options(self, options):
        if 'format' not in options:
            options.format = 'json'

        if 'result' not in options:
            options.output = None

        if 'porcelain' not in options:
            options.porcelain = False

        if 'silent' not in options:
            options.silent = True

        if 'read' not in options:
            options.read = False

        return options

    def run(self):
        result = None

        if self.options.read:
            result = Result.from_file(self.endpoint)
        else:
            try:
                self.client = Client(self.endpoint)
            except EndpointNotReachableException:
                Output.message('Endpoint {} is not reachable, aborting validation.', self.endpoint)
                exit(1)
            except EndpointIsNotAnOParlEndpointException:
                Output.message('Endpoint {} is not an OParl-Endpoint, aborting validation.', self.endpoint)
                exit(1)

            result = self.validate()
            result.compile()

        self.handle_result(result)

    def validate(self):
        Output.message("Beginning validation of {}", self.endpoint)
        Output.message("Found '{}'", self.client.system.get_name())

        bodies = self.client.system.get_body()
        num_bodies = len(bodies)

        unprocessed_entities = EntityQueue(maxsize = self.ENTITY_QUEUE_SIZE)

        seen_list = SeenList()
        result = Result()

        walker_threads = []
        worker_threads = []

        for body in bodies:
            walker = self.client.create_body_walker(body, unprocessed_entities)
            walker_threads.append(walker)

        for thread in walker_threads:
            thread.start()

        # let the walkers walk a little
        while unprocessed_entities.empty():
            pass

        # TODO: make this dependent on system resources / an option

        Output.add_progress_bar('validation_progress', 'Validating')

        for i in range(0, Validator.NUM_VALIDATION_WORKERS):
            worker = ValidationWorker(
                'validation_worker_{}'.format(i),
                unprocessed_entities,
                seen_list,
                result
            )
            worker_threads.append(worker)

        for thread in worker_threads:
            thread.start()

        for thread in walker_threads:
            thread.join()

        while not unprocessed_entities.empty():
            pass

        for thread in worker_threads:
            thread.join()

        Output.message("Validation finished")

        result.network = self.client.network
        result.total_entities = len(seen_list)

        return result

    def handle_result(self, result):
        formatted_result = result.text()
        if self.options.format == 'json':
            formatted_result = result.json()

        if Output.porcelain or self.options.result is not None:
            with open(self.options.result, 'w+') as f:
                f.write(formatted_result)
                exit(0)

        print(formatted_result)


class ValidationWorker(Thread):
    def __init__(self, id, queue, seen_list, result):
        super(ValidationWorker, self).__init__()
        self.id = id
        self.queue = queue
        self.result = result
        self.seen_list = seen_list
        self.current_object = None

    def run(self):
        while not self.queue.empty():
            self.get_next_object()

            if not self.is_seen_object():
                try:
                    results = self.validate_object()
                    self.save_validation_results(results)
                except ObjectValidationFailedException:
                    self.save_failed_object()

                Output.update_progress_bar('validation_progress', remaining=self.queue.qsize())

    def get_next_object(self):
        self.queue.acquire()
        self.current_object = self.queue.get()
        self.queue.release()

    def is_seen_object(self):
        if self.current_object.get_id() in self.seen_list:
            return True

        self.seen_list.push(self.current_object.get_id())

        return False

    def validate_object(self):
        try:
            validation_results = self.current_object.validate()
        except GLib.Error as glib_error:
            raise ObjectValidationFailedException from glib_error

        # TODO: implement additional checks like e.g. file reachability

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