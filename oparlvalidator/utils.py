from collections import MutableMapping


class LazyDict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.__model = dict(*args, **kwargs)
        self.__cache = dict()

    def __getitem__(self, item):
        if item not in self.__cache:
            value = self.__model[item]
            value = value() if callable(value) else value
            self.__cache[item] = value
            return value
        else:
            return self.__cache[item]

    def get(self, item, default=None):
        try:
            return self.__getitem__(item)
        except KeyError:
            return default

    def __str__(self):
        return "<LazyDict - Keys: %s>" % str([x for x in self])

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.__model)

    def __len__(self):
        return len(self.__model)

    def __delitem__(self, key):
        del self.__model[key]
        if key in self.__cache:
            del self.__cache[key]

    def __setitem__(self, key, value):
        self.__model[key] = value
        if key in self.__cache:
            del self.__cache[key]

    def realize(self):
        '''
        Goes through whole LazyDict and makes a dict out of the keys
        and retrieved values. If the LazyDict is nested, it will also
        iterate through the subsequent LazyDict.

        :returns: dict - dict representation of whole LazyDict.
        '''
        d = {}
        for k, v in self.items():
            if isinstance(v, LazyDict):
                d[k] = v.realize()
            else:
                d[k] = v
        return d

    def invalidate(self, key=None):
        if key is not None:
            if key in self.__cache:
                del self.__cache[key]
            else:
                raise KeyError()
        else:
            self.__cache = dict()
