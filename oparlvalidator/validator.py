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

        type_check = {
            'type': 'object',
            'properties': {
                '@type': {
                    'type': 'string',
                    'enum': OPARL.keys()  # check if we have a schema for @type
                }
            }
        }

        Draft4Validator(type_check).validate(self.data)

        obj_type = self.data['@type']
        Draft4Validator(OPARL[obj_type]).validate(self.data)
        return True
