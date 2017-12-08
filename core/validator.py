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

from core.client import Client
from core.entity_queue import EntityQueue
from core.exceptions import \
    EndpointNotReachableException, \
    EndpointIsNotAnOParlEndpointException
from core.output import Output
from core.pool import Pool
from core.result import Result
from core.seen_list import SeenList
from core.validation_worker import ValidationWorker

# TODO: Auto-update this line via .gitattributes
VALIDATOR_VERSION = '0.9'

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

    # TODO: these should be options
    NUM_VALIDATION_WORKERS = 3
    ENTITY_QUEUE_SIZE = 1000

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
        Output.add_progress_bar('validation_progress', 'Validating')

        bodies = self.client.system.get_body()
        num_bodies = len(bodies)

        unprocessed_entities = EntityQueue(maxsize = self.ENTITY_QUEUE_SIZE)

        seen_list = SeenList()
        result = Result()
        check_pool = Pool()

        walker_threads = []
        worker_threads = []

        for body in bodies:
            walker = self.client.create_body_walker(body, unprocessed_entities)
            walker_threads.append(walker)

        for i in range(0, Validator.NUM_VALIDATION_WORKERS):
            worker = ValidationWorker(
                'validation_worker_{}'.format(i),
                unprocessed_entities,
                seen_list,
                check_pool,
                result
            )
            worker_threads.append(worker)

        for thread in walker_threads:
            thread.start()

        # let the walkers walk a little
        while unprocessed_entities.empty():
            pass

        for thread in worker_threads:
            thread.start()

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
                Output.message('Result has been written to {} as {}.', self.options.result, self.options.format)
                exit(0)

        print(formatted_result)

def get_validator_version():
    return VALIDATOR_VERSION
