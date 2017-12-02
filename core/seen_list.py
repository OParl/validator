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

import time
import redis

class SeenList(object):
    def __init__(self, redis_server='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_server, port=redis_port, db=0)
        self.seen = 'OParlValidator_SeenList_' + int(time.time())

    def __contains__(self, key):
        return key in self.seen

    def __len__(self):
        return self.redis.llen(self.seen)

    def push(self, item):
        self.redis.lpush(self.seen, item)

    def pop(self):
        return self.redis.lpop(self.seen)
