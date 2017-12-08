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

from functools import reduce
from queue import Queue
from threading import Lock

class EntityQueue:
    def __init__(self, maxsize = 1000):
        self.queue = Queue(maxsize)
        self.enqueuing_flags = {}

    def put(self, item, block = True, timeout = None):
        self.queue.put(item, block, timeout=timeout)

    def get(self, block = True, timeout = None):
        return self.queue.get(block, timeout)

    def qsize(self):
        return self.queue.qsize()

    def empty(self):
        return self.queue.empty() # and not self.is_enqueuing()

    def full(self):
        return self.queue.full()

    def add_enqueuing_flag(self, id):
        self.enqueuing_flags[id] = True

    def update_enqueuing_flag(self, id, state):
        self.enqueuing_flags[id] = state

    def is_enqueuing(self):
        is_enqueuing = True

        for flag in self.enqueuing_flags.values():
            is_enqueuing = is_enqueuing or flag

        return is_enqueuing
