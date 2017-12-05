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

from math import floor, log2
from random import randint
from time import sleep
from threading import Thread

from core.utils import sha1_hexdigest
from core.output import Output
from core.seen_list import SeenList

class BodyWalker(Thread):
    def __init__(self, client, body, queue):
        super(BodyWalker, self).__init__()
        self.client = client
        self.body = body
        self.queue = queue
        self.done = False
        self.seen_list = SeenList()

    def connect_signals(self):
        incoming_signals = [
            'incoming_organizations',
            'incoming_meetings',
            'incoming_papers',
            'incoming_persons'
        ]

        for incoming_signal in incoming_signals:
            self.body.connect(incoming_signal, self.handle_incoming)

    def run(self):
        progress_id = sha1_hexdigest(self.body.get_id())
        #Output.add_progress_bar(progress_id, 'Fetching from \'{}\''.format(self.body.get_name()))

        self.connect_signals()

        try:
            self.body.get_neighbors()
        except GLib.Error:
            Output.message('Body {} failed to provide entities', self.body.get_id())
            return

        total_neighbors = len(self.seen_list)

        #Output.update_progress_bar(progress_id, remaining=total_neighbors - index - 1)

        self.queue.acquire()
        self.queue.put(self.body)
        self.queue.release()

        Output.message("Fetched {} objects from {}", total_neighbors + 1, self.body.get_id())

    def handle_incoming(self, body, object_list):
        num_new_objects = len(object_list)
        Output.message('Received {} new objects from {}', num_new_objects, body.get_name())

        sleep_count = 0
        for index, entity in enumerate(object_list):
            if not self.queue.full():
                if not self.is_seen_entity(entity):
                    self.queue.acquire()
                    self.queue.put(entity)
                    self.queue.release()
            else:
                sleep_count += 1
                sleep_time = floor(log2(sleep_count))
                Output.message('Queue full, waiting {} second(s)', sleep_time)
                sleep(sleep_time)


    # NOTE: this is very similar to ValidationWorker.is_seen_object...
    def is_seen_entity(self, entity):
        if entity.get_id() in self.seen_list:
            return True

        self.seen_list.push(entity.get_id())

        return False