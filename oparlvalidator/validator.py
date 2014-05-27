# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from jsonschema.validators import Draft4Validator
from .schema import OPARL


class OParl(object):

    def __init__(self, string):
        self.string = string
        self.data = json.loads(string)

    def validate(self):
        Draft4Validator(OPARL).validate(self.data)
        return True  # Maybe
