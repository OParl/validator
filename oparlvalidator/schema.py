# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

# As a rare exception. I think it’ll be helpful to use double quotes for
# the schema, so it doubles as JSON. Mind the commas.

OPARL = {
    "id": "http://some.site.somewhere/entry-schema#",  # TODO
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "OParl schema",
    "type": "object",
    "properties": {
        "anyOf": [
            {"$ref": "#/definitions/system"},
            {"$ref": "#/definitions/body"},
            {"$ref": "#/definitions/organization"},
            {"$ref": "#/definitions/person"},
            {"$ref": "#/definitions/meeting"},
            {"$ref": "#/definitions/agendaItem"},
            {"$ref": "#/definitions/paper"},
            {"$ref": "#/definitions/document"},
            {"$ref": "#/definitions/consultation"},
            {"$ref": "#/definitions/location"},
            {"$ref": "#/definitions/membership"}
        ]
    },
    "definitions": {
        "system": {},  # TODO: Move newObjects, updatedObjects,
                       # and removedObjects
        "body": {},
        "organization": {},
        "person": {},
        "meeting": {},
        "agendaItem": {},
        "paper": {},
        "document": {},
        "consultation": {},
        "location": {},
        "membership": {
            "type": "object",
            "properties": {
                "person": {
                    "type": "string",
                    "format": "uri"
                },
                "organization": {
                    "type": "string",
                    "format": "uri"
                },
                "role": {
                    "type": "string"
                },
                "post": {
                    "type": "string"
                },
                "onBehalfOf": {
                    "type": "string",
                    "format": "uri"
                },
                "startDate": {
                    "type": "string",
                    "format": "date-time"
                },
                "endDate": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "person",
                "organization"
            ]
        }
    }
}

