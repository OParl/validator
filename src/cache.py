import hashlib
import redis

class Cache:
    basekey = ""
    ttl = 300
    rclient = None

    def __init__(self, url, ttl=300, redis_server='localhost', redis_port=6379):
        self.basekey = hashlib.sha1(url.encode('ascii'))
        self.ttl = ttl
        self.rclient = redis.ConnectionPool(host=redis_server, port=redis_port, db=0)
