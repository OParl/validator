# The MIT License (MIT)
#
# Copyright (c) 2017 Stefan Graupner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import redis

class Cache:
    basekey = ""
    ttl = 300

    def __init__(self, basekey="", ttl=300):
        self.basekey = basekey
        self.ttl = ttl

    def has(self, key):
        return False

    def get(self, key):
        return ""

    def set(self, key, value, ttl=300):
        pass

    def fullkey(self, key):
        if len(self.basekey) > 0:
            return "{}:{}".format(self.basekey, key)
        else:
            return key

class RedisCache(Cache):
    redis = None

    def __init__(self, basekey="", ttl=300, redis_server='localhost', redis_port=6379):
        Cache.__init__(self, basekey, ttl)
        self.redis = redis.Redis(host=redis_server, port=redis_port, db=0)

    def has(self, key):
        return self.redis.exists(self.fullkey(key))

    def get(self, key):
        return self.redis.get(self.fullkey(key))

    def set(self, key, value, ttl=300):
        return self.redis.set(self.fullkey(key), value, ttl)
