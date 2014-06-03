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
        'system': {
            'type': 'object',
            'properties': {
                '@type': {
                    'type': 'string'
                },
                '@id': {
                    'type': 'string'
                },
                'oparlVersion': {
                    'type': 'string'
                },
                'name': {
                    'type': 'string'
                },
                'website': {
                    'type': 'string',
                    'format': 'uri'
                },
                'contactEmail': {
                    'type': 'string'
                },
                'contactName': {
                    'type': 'string'
                },
                'vendor': {
                    'type': 'string',
                    'format': 'uri'
                },
                'product': {
                    'type': 'string',
                    'format': 'uri'
                },
                'bodies': {
                    'type': 'string'
                },
                'newObjects': {
                    'type': 'string',
                    'format': 'uri'
                },
                'updatedObjects': {
                    'type': 'string',
                    'format': 'uri'
                },
                'removedObjects': {
                    'type': 'string',
                    'format': 'uri'
                }
            },
            'required': [
                '@type',
                '@id',
                'oparlVersion',
                'bodies'
            ],
        },
        'body': {
            'type': 'object',
            'properties': {
                '@type': {
                    'type': 'string'
                },
                '@id': {
                    'type': 'string'
                },
                'system': {
                    '$ref': '#/definitions/system'
                },
                'name': {
                    'type': 'string'
                },
                'nameLong': {
                    'type': 'string'
                },
                'website': {
                    'type': 'string',
                    'format': 'uri'
                },
                'license': {
                    'type': 'string',
                    'format': 'uri'
                },
                'licenseValidSinceDay': {
                    'type': 'date-time'
                },
                'rga': {
                    'type': 'string'
                },
                'equivalentBody': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'format': 'uri'
                    }
                },
                'contactEmail': {
                    'type': 'string'
                },
                'contactName': {
                    'type': 'string'
                },
                'paper': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/paper'
                    }
                },
                'member': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/person'
                    }
                },
                'meeting': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/meeting'
                    }
                },
                'organization': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/organization'
                    }  
                },
                'keyword': {
                    'type': 'string' # skos:Concept
                },
                'allConcepts': {
                    'type': 'string' # skos:Concept
                },
                'created': {
                    'type': 'date-time'
                },
                'lastModified': {
                    'type': 'date-time'
                }
            },
            'required': [
                '@type',
                '@id',
                'system',
                'name',
                'paper',
                'member',
                'meeting',
                'organization'
            ],
        },
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

