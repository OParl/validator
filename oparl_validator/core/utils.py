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
import hashlib

def camelize_snake(string):
    parts = string.split('_')
    return ''.join(map(lambda part: part.title(), parts))

def get_base_classes_from_instance(class_instance):
    bases = []

    for base in class_instance.__class__.__bases__:
        name = base.__name__
        module = base.__module__
        bases.append('{}.{}'.format(module, name))

    return bases

def get_oparl_version_from_object(oparl_object):
    return oparl_object.get_oparl_type().split('/')[-2]


def get_entity_type_from_object(oparl_object):
    return oparl_object.get_oparl_type().split('/')[-1]


def sha1_hexdigest(string):
    string = str(string).encode('utf_8')

    return hashlib.sha1(string).hexdigest()
