# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from os.path import dirname, join

with open(join(dirname(__file__), 'schema.json')) as json_file:
    OPARL = json.load(json_file)

# Additional validation functions here

def test_must_have_mailto_prefix(str):
    """
    email address must be prefixed with "mailto:"
    """
    pass    # TODO: [RB|Jun 5, 2014|todo] implement

def test_is_valid_email(str):
    """
    check for valid email address
    """
    pass    # TODO: [RB|Jun 5, 2014|todo] implement