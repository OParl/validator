# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

OPARL_SCHEMAS = {
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
            ]
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
                    'type':'string',
                    'format':'uri',
                    'oparl:linksTo':'system'
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
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'paper'
                    }
                },
                'member': {
                    'type': 'array',
                    'items': {
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'person'
                    }
                },
                'meeting': {
                    'type': 'array',
                    'items': {
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'meeting'
                    }
                },
                'organization': {
                    'type': 'array',
                    'items': {
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'organization'
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
            ]
        },
        'organization': {
            'type': 'object',
            'properties': {
                # @context?
                '@type': {
                    'type': 'string'
                },
                '@id': {
                    'type': 'string'
                },
                'body': {
                    'type':'string',
                    'format':'uri',
                    'oparl:linksTo':'body'
                },
                'nameLong': {
                    'type': 'string'
                },
                'nameShort': {
                    'type': 'string'
                },
                'post': {
                    'type': 'array',
                    'items': {
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'post'
                    }
                },
                'member': {
                    'type': 'array',
                    'items': {
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'person'
                    }
                },
                'subOrganizationOf': {
                    'type':'string',
                    'format':'uri',
                    'oparl:linksTo':'organization'
                },
                'organiziationType': {
                    'type': 'string'    # skos:Concept
                },
                'keyword': {
                    'type': 'array',
                    'items':{
                        'type': 'string'
                    }
                },
                'created': {
                    'type': 'date-time'
                },
                'modified': {
                    'type': 'date-time'
                }
            },
            'required': [
                '@type',
                '@id',
                'body',
                'nameLong',
                'member'
            ]
        },
        'person': {
            'type': 'object',
            'properties': {
                # @context?
                '@type': {
                    'type': 'string'    # ^oparl:Person$
                },
                '@id': {
                    'type': 'string'    # IRI?
                },
                'name': {
                    'type': 'string'
                },
                'familyName': {
                    'type': 'string'
                },
                'formOfAddress': {
                    'type': 'string'    # skos:Concept
                },
                'title': {
                    'type': 'array',
                    'items': {
                        'type': 'string'    # skos:Concept
                    }
                },
                'gender': {
                    'type': 'string'    # "Kardinalität 0 bis *" ??
                },
                'phone': {
                    'type': 'string'    # ^tel:\+?\d+$
                },
                'email': {
                    'type': 'string'    # ^mailto:$ + email-address
                },
                'streetAddress': {
                    'type': 'string'
                },
                'postalCode': {
                    'type': 'string'
                },
                'locality': {
                    'type': 'string'    # vcard:locality
                },
                'organization': {
                    'type': 'array',
                    'items': {
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'organization'
                    }
                },
                'status': {
                    'type': 'array',
                    'items': {
                        'type': 'string'    # skos:Concept
                    }
                },
                'hasMembership': {
                    'type': 'array',
                    'items': {
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'membership'
                    }
                },
                'keyword': {
                    'type': 'array',
                    'items': {
                        'type': 'string'    # skos:Concept
                    }
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
                'name'
            ]
        },
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
                    'type':'string',
                    'format':'uri',
                    'oparl:linksTo':'location',
                },
                'organization': {
                    'type':'string',
                    'format':'uri',
                    'oparl:linksTo':'location',
                },
                'participant': {
                    'type': 'array',
                    'items': {
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'person',
                    },
                },
                'invitation': {
                    'type':'string',
                    'format':'uri',
                    'oparl:linksTo':'document',
                },
                'resultsProtocol': {
                    'type':'string',
                    'format':'uri',
                    'oparl:linksTo':'document',
                },
                'verbatimProtocol': {
                    'type':'string',
                    'format':'uri',
                    'oparl:linksTo':'document',
                },
                'auxiliaryDocument': {
                    'type': 'array',
                    'items': {
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'document',
                    },
                },
                'agendaItem': {
                    'type': 'array',
                    'items': {
                        'type':'string',
                        'format':'uri',
                        'oparl:linksTo':'agendaItem',
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
            ]
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

