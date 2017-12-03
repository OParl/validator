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

from .client import Client
from .entity_queue import EntityQueue
from .exceptions import EndpointNotReachableException, EndpointIsNotAnOParlEndpointException
from .output import Output
from .result import Result
from .seen_list import SeenList

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

        try:
            self.client = Client(endpoint)
        except EndpointNotReachableException:
            Output.message('Endpoint {} is not reachable, aborting validation.', endpoint)
            exit(1)
        except EndpointIsNotAnOParlEndpointException:
            Output.message('Endpoint {} is not an OParl-Endpoint, aborting validation.', endpoint)
            exit(1)

    def parse_options(self, options):
        # TODO: implement schema validation
        # if 'validate_schema' not in options:
        #     options.validate_schema = False

        if 'format' not in options:
            options.format = 'json'

        if 'result' not in options:
            options.output = None

        if 'porcelain' not in options:
            options.porcelain = False

        if 'silent' not in options:
            options.silent = True

        return options

    def validate(self):
        Output.message("Beginning validation of {}", self.endpoint)
        Output.message("Found '{}'", self.client.system.get_name())

        bodies = self.client.system.get_body()
        num_bodies = len(bodies)

        unprocessed_entities = EntityQueue(maxsize = 1000)

        seen_list = SeenList()
        result = Result()

        walker_threads = []
        worker_threads = []

        for body in bodies:
            walker = self.client.create_body_walker(body, unprocessed_entities)
            walker_threads.append(walker)

        for thread in walker_threads:
            thread.start()

        # TODO: there's most likely a better solution than this
        sleep(5) # let walkers walk a little

        # TODO: if theres nothing in the queue by now, the oparl server
        #       is way too slow, is this a validation error?

        # TODO: make this dependent on system resources / an option
        for i in range(0, Validator.NUM_VALIDATION_WORKERS):
            worker = ValidationWorker(
                i,
                unprocessed_entities,
                seen_list,
                result
            )
            worker_threads.append(worker)

        for thread in worker_threads:
            thread.start()

        while not unprocessed_entities.empty():
            pass

        for thread in worker_threads:
            thread.join()

        Output.message("Validation finished")

        result.network = self.client.network
        result.total_entities = len(seen_list)

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

    def run(self):
        while not self.queue.empty():
            self.queue.acquire()
            oparl_object = self.queue.get()
            self.queue.release()

            if oparl_object.get_id() in self.seen_list:
                continue

            self.seen_list.push(oparl_object.get_id())
            self.validate_object(oparl_object)

    def validate_object(self, oparl_object):
        try:
            validation_results = oparl_object.validate()
        except GLib.Error:
            # TODO: track liboparl validation errors
            validation_results = []

        # TODO: implement additional checks like e.g. file reachability

        self.result.acquire()

        if len(validation_results) > 0:
            self.result.failed_entities += 1

        for result in validation_results:
            self.result.parse_validation_result(oparl_object, result)

        self.result.release()
