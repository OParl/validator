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

from threading import activeCount, Thread
from time import sleep

from .cache import Cache
from .client import Client
from .entity_queue import EntityQueue
from .exceptions import *
from .output import Output
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
        self.seen_list = SeenList()

        Output.porcelain = self.options.porcelain
        Output.silent = self.options.silent
        Output.initialize()

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

        if 'silent' not in options:
            options.silent = True

        if 'porcelain' not in options:
            options.porcelain = False

        if 'format' not in options:
            options.format = 'json'

        return options

    def validate(self):
        Output.message("Beginning validation of {}", self.endpoint)
        Output.message("Found '{}'", self.client.system.get_name())

        bodies = self.client.system.get_body()
        num_bodies = len(bodies)

        unprocessed_entities = EntityQueue(maxsize = 1000)

        walker_threads = []
        worker_threads = []

        for body in bodies:
            walker = self.client.create_body_walker(body, unprocessed_entities)
            walker_threads.append(walker)

        for thread in walker_threads:
            thread.start()

        # TODO: there's most likely a better solution than this
        sleep(2) # let walkers walk a little

        # TODO: if theres nothing in the queue by now, the oparl server
        #       is way too slow, is this a validation error?

        # TODO: make this dependant on system resources / an option
        for i in range(0, Validator.NUM_VALIDATION_WORKERS):
            worker = ValidationWorker(i, unprocessed_entities, self.seen_list)
            worker_threads.append(worker)

        for thread in worker_threads:
            thread.start()

        while not unprocessed_entities.empty():
            pass

        for thread in worker_threads:
            thread.join()

        Output.message("Validation finished")


class ValidationWorker(Thread):
    def __init__(self, id, queue, seen_list):
        super(ValidationWorker, self).__init__()
        self.id = id
        self.queue = queue
        self.seen_list = seen_list

    def run(self):
        while not self.queue.empty():
            self.queue.acquire()
            oparl_object = self.queue.get()
            self.queue.release()

            if oparl_object.get_id() in self.seen_list:
                continue

            self.seen_list.push(oparl_object.get_id())

            validation_result = oparl_object.validate()
