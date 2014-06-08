# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from os.path import dirname, join

with open(join(dirname(__file__), 'schema.json')) as json_file:
    OPARL = json.load(json_file)

# Additional validation functions here
