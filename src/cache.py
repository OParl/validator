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

"""
    Object Cache for the Validator

    Upon the first succesful retrieval of an OParl entity by the validator
    it will be stored in the cache for a certain amount of time to reduce
    load on the endpoint, eliminate network latency and speed up the validation
    process.
"""


class Cache:
    """ the cache's base key """
    basekey = ""

    hits = 0
    misses = 0
    lookups = 0

    def __init__(self, basekey=""):
        """
            Initialize a Cache instance

            Caches can preprend a basekey to every cached item.
            This makes it possible to use one cache provider (i.e. Redis)
            with multiple Cache instances
        """
        self.basekey = basekey

    def has(self, key):
        """ Check wether a key exists """
        return False

    def get(self, key):
        """ Get the contents of a key """
        return ""

    def set(self, key, value, ttl=0):
        """
            Set the contents of a key

            This allows to optionally set the time this cache item will be kept
        """
        pass

    def fullkey(self, key):
        """
            Get the full key name of a key

            This will preprend the key with the Cache instance's base key value
        """
        if len(self.basekey) > 0:
            return "{}:{}".format(self.basekey, key)
        else:
            return key


class RedisCache(Cache):
    redis = None

    def __init__(self, basekey="", redis_server='localhost', redis_port=6379):
        import redis

        Cache.__init__(self, basekey)
        self.redis = redis.Redis(host=redis_server, port=redis_port, db=0)

    def has(self, key):
        self.lookups += 1
        result = self.redis.exists(self.fullkey(key))

        if result:
            self.hits += 1
        else:
            self.misses += 1

        return result

    def get(self, key):
        self.lookups += 1

        result = self.redis.get(self.fullkey(key))

        if result:
            self.hits += 1
        else:
            self.misses += 1

        return result

    def set(self, key, value, ttl=3600):
        return self.redis.set(self.fullkey(key), value, ttl)
