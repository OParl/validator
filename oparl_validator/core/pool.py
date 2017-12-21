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

from glob import glob
from importlib import import_module

from oparl_validator.core.utils import camelize_snake, get_base_classes_from_instance

class Pool:
    """
        Collect all extra checks and provide them in a pool
        for easy use across validation worker threads.^
    """

    def __init__(self):
        self.checks = {}
        check_files = glob('extra/check_*.py')
        for check_file in check_files:
            class_instance = self.load_class_from_file(check_file)

            if not self.is_check(class_instance):
                continue

            self.add_check(class_instance)


    def load_class_from_file(self, filename):
        module_name, class_name = self.extract_loading_info(filename)

        module = import_module(module_name)
        class_definition = getattr(module, class_name)
        class_instance = class_definition()

        return class_instance

    def extract_loading_info(self, filename):
        module_name = filename.split('.py')[0].replace('/', '.')
        class_name = camelize_snake(module_name.split('.')[1])

        return (module_name, class_name)

    def is_check(self, class_instance):
        return 'core.check.Check' in get_base_classes_from_instance(class_instance)

    def add_check(self, class_instance):
        entity = class_instance.evaluates_entity_type()
        if not entity in self.checks.keys() or type(self.checks[entity]) is not 'list':
            self.checks[entity] = []

        self.checks[entity].append(class_instance)

    def get_checks_for_type(self, type : str):
        type = type.lower()

        if type in self.checks.keys():
            return self.checks[type]

        return []