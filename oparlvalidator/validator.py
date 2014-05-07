# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from schematics.models import Model

class OParl(object):

    def __init__(self, string):
        self.string = string
        self.data = json.loads(string)

    def validate(self):
        raise Exception('Ponies!')
