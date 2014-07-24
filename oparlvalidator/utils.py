from collections import MutableMapping
from os.path import join, dirname, splitext


SCHEMA_DIR = join(dirname(__file__), 'schema')


def build_object_type(object_name):
    basedomain = 'http://oparl.org/schema/'
    if object_name.startswith(basedomain):
        return 'schema/%s' % object_name[len(basedomain):]

    if object_name.startswith(SCHEMA_DIR):
        filename = splitext(object_name)[0]
        return 'schema%s' % filename[len(SCHEMA_DIR):]

    return object_name


def import_from_string(path):
    path_parts = path.split(':')
    if len(path_parts) != 2:
        raise ImportError('path must be in the form of '
                          'pkg.module.submodule:attribute')
    module = __import__(path_parts[0], fromlist=path_parts[1])

    if not hasattr(module, path_parts[1]):
        # the caller only needs to handle ImportError, so we prevent a
        # AttributeError by raising a custom exception
        raise ImportError("'%s' object has no attribute '%s'" %
                          tuple(path_parts))

    return getattr(module, path_parts[1])


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
