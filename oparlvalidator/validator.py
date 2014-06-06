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
        try:
            obj_type = self.data['@type']
            Draft4Validator(OPARL[obj_type]).validate(self.data)
            return True

        except Exception as e:
            raise e
