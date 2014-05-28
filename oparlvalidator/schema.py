# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

OPARL = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'description': 'OParl schema',
    'type': 'object',
    'properties': {
        'system': {
            'type': {'$ref': '#/definitions/system'},
        },
        'body': {
            'type': {'$ref': '#/definitions/body'},
        },
        'organization': {
            'type': {'$ref': '#/definitions/organization'},
        },
        'person': {
            'type': {'$ref': '#/definitions/person'},
        },
        'meeting': {
            'type': {'$ref': '#/definitions/meeting'},
        },
        'agendaItem': {
            'type': {'$ref': '#/definitions/agendaItem'},
        },
        'paper': {
            'type': {'$ref': '#/definitions/paper'},
        },
        'document': {
            'type': {'$ref': '#/definitions/document'},
        },
        'consultation': {
            'type': {'$ref': '#/definitions/consultation'},
        },
        'location': {
            'type': {'$ref': '#/definitions/location'},
        },
        'membership': {
            'type': {'$ref': '#/definitions/membership'},
        },
    },
    'definitions': {
        'system': {},  # TODO: Move newObjects, updatedObjects,
                       # and removedObjects
        'body': {},
        'organization': {},
        'person': {},
        'meeting': {
            'type': 'object',
            'properties': {
                '@context': {},
                '@type': {
                    'type': 'string',
                },
                '@id': {
                    'type': 'string',
                },
                'name': {
                    'type': 'string',
                },
                'start': {
                    'type': 'date-time',
                },
                'end': {
                    'type': 'date-time',
                },
                'location': {
                    '$ref': '#/definitions/location',
                },
                'organization': {
                    '$ref': '#/definitions/location',
                },
                'participant': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/person',
                    },
                },
                'invitation': {
                    '$ref': '#/definitions/document',
                },
                'resultsProtocol': {
                    '$ref': '#/definitions/document',
                },
                'verbatimProtocol': {
                    '$ref': '#/definitions/document',
                },
                'auxiliaryDocument': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/document',
                    },
                },
                'agendaItem': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/agendaItem',
                    },
                },
                'created': {
                    'type': 'date-time',
                },
                'modified': {
                    'type': 'date-time',
                },
            },
            'required': [
                '@context',
                '@id',
                '@type',
                'name',
                'organization',
                'participant',
                'start',
            ],
        },
        'agendaItem': {},
        'paper': {},
        'document': {},
        'consultation': {},
        'location': {},
        'membership': {
            'type': 'object',
            'properties': {
                'person': {
                    'type': 'string',
                    'format': 'uri'
                },
                'organization': {
                    'type': 'string',
                    'format': 'uri'
                },
                'role': {
                    'type': 'string'
                },
                'post': {
                    'type': 'string'
                },
                'onBehalfOf': {
                    'type': 'string',
                    'format': 'uri'
                },
                'startDate': {
                    'type': 'string',
                    'format': 'date-time'
                },
                'endDate': {
                    'type': 'string',
                    'format': 'date-time'
                }
            },
            'required': [
                'person',
                'organization'
            ]
        }
    }
}

