# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unittest
from os.path import join
from .. import utils


class TestBuildObjectType(unittest.TestCase):

    def test_build_object_type(self):
        self.assertEquals(
            utils.build_object_type('http://oparl.org/schema/1.0/Document'),
            'schema/1.0/Document')
        self.assertEquals(
            utils.build_object_type('schema/1.0/Document'),
            'schema/1.0/Document')
        self.assertEquals(
            utils.build_object_type(
                join(utils.SCHEMA_DIR, '1.0', 'Document')),
            'schema/1.0/Document')
        self.assertEquals(
            utils.build_object_type(
                join(utils.SCHEMA_DIR, '1.0', 'Document.json')),
            'schema/1.0/Document')
        self.assertEquals(
            utils.build_object_type(
                join(utils.SCHEMA_DIR, '1.0', 'AgendaItem.json')),
            'schema/1.0/AgendaItem')


class TestImportFromString(unittest.TestCase):

    def setUp(self):
        self.called = 0

    def should_be_called(self):
        self.called += 1

    def test_import(self):
        imported = utils.import_from_string(
            '%s:%s' % (self.__module__, self.__class__.__name__))
        imported.should_be_called(self)
        self.assertEquals(1, self.called)

    def test_invalid_fromat(self):
        with self.assertRaises(ImportError):
            utils.import_from_string('test')

        with self.assertRaises(ImportError):
            utils.import_from_string('test:test:test')

    def test_missing_import(self):
        with self.assertRaises(ImportError):
            utils.import_from_string(
                'a%s:%s' % (self.__module__, self.__class__.__name__))

        with self.assertRaises(ImportError):
            utils.import_from_string(
                '%s:a%s' % (self.__module__, self.__class__.__name__))


class TestLazyDict(unittest.TestCase):

    def setUp(self):
        self.dict = utils.LazyDict()

    def test_realy_lazy(self):
        self.dict['a'] = (lambda: self.assertTrue(False), 'this is a test')

    def test_works(self):
        self.dict['a'] = (lambda: 'this is a test')
        self.assertEquals('this is a test', self.dict['a'])

    def test_get(self):
        self.dict['a'] = (lambda: 'this is a test')
        self.assertEquals('this is a test', self.dict.get('a'))
        self.assertEquals('only a test', self.dict.get('b', 'only a test'))

    def test_reset(self):
        self.dict['a'] = (lambda: 'this is a test')
        self.assertEquals('this is a test', self.dict['a'])
        self.dict['a'] = (lambda: 'only a test')
        self.assertEquals('only a test', self.dict['a'])

    def test_realize(self):
        self.dict['a'] = (lambda: 'test1')
        self.dict['b'] = (lambda: 'test2')
        self.assertEquals({'a': 'test1', 'b': 'test2'}, self.dict.realize())

    def test_caching(self):
        def test():
            self.assertFalse(called[0], 'Should only be called once')
            called[0] = True
            return 'this is a test'

        # this is a list, so that the inner function can change the value
        called = [False]

        self.dict['a'] = test
        self.assertEquals('this is a test', self.dict['a'])
        self.assertEquals('this is a test', self.dict['a'])

    def test_invalidate(self):
        def test():
            called[0] += 1
            return 'this is a test'

        # this is a list, so that the inner function can change the value
        called = [0]

        self.dict['a'] = test
        self.assertEquals('this is a test', self.dict['a'])
        self.dict.invalidate()
        self.assertEquals('this is a test', self.dict['a'])
        self.assertEquals(2, called[0])

    def test_invalidate_key(self):
        def test1():
            called[0] += 1
            return 'this is a test'

        def test2():
            called[1] += 1
            return 'this is a test'

        # this is a list, so that the inner function can change the value
        called = [0, 0]

        self.dict['a'] = test1
        self.dict['b'] = test2
        self.assertEquals('this is a test', self.dict['a'])
        self.assertEquals('this is a test', self.dict['b'])
        self.dict.invalidate('a')
        self.assertEquals('this is a test', self.dict['a'])
        self.assertEquals('this is a test', self.dict['b'])
        self.assertEquals([2, 1], called)

    def test_delete(self):
        self.dict['a'] = (lambda: self.assertTrue(False), 'this is a test')
        del self.dict['a']
        self.assertFalse('a' in self.dict)

    def test_delete_after_call(self):
        self.dict['a'] = (lambda: 'this is a test')
        self.assertEquals('this is a test', self.dict['a'])
        del self.dict['a']
        self.assertFalse('a' in self.dict)

    def test_missing_key(self):
        self.assertRaises(KeyError, (lambda: self.dict['a']))

    def test_invalidate_missing_key(self):
        with self.assertRaises(KeyError):
            self.dict.invalidate('a')
