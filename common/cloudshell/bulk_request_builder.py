import os
import jsonpickle
import json
import jsonschema
from common.cloudshell.connectivity_schema import DriverRequest, BaseObject
import python_jsonschema_objects as pjs


class BulkRequestBuilder(object):
    def __init__(self):
        schemas_dir = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(schemas_dir, 'set_vlan_schema.json')) as file_object:
            self.schema = jsonpickle.decode(file_object.read())
        self.resolver = jsonschema.RefResolver('file://' + schemas_dir + '/', self.schema)

        self.actions = []

    def append_action(self, action):
        self.actions.append(action)

    def get_request(self):
        obj_tovalidate = BaseObject()
        request = DriverRequest()
        request.actions = self.actions
        obj_tovalidate.driverRequest = request
        obj_as_dict = jsonpickle.decode(jsonpickle.encode(obj_tovalidate))

        jsonschema.Draft4Validator(SET_VLAN_SCHEMA, resolver=self.resolver).validate(obj_tovalidate.__dict__)

        return jsonpickle.encode(obj_as_dict, unpicklable=False)

    @staticmethod
    def create_inctances():
        #        schemas = {}
        #        schemas_dir = os.path.dirname(os.path.realpath(__file__))
        #        for file_name in os.listdir(schemas_dir):
        #            if file_name.endswith('.json'):
        #                with open(os.path.join(schemas_dir, file_name)) as file_object:
        #                    schema = jsonpickle.decode(file_object.read())
        #                    schemas[file_name] = schema

        builder = pjs.ObjectBuilder(schema_uri=SET_VLAN_SCHEMA,
                                    resolved=[BASE_SCHEMA])

        ns = builder.build_classes()

        print 'done'


SET_VLAN_SCHEMA = {
    # "$schema": "http://json-schema.org/draft-04/schema#",
    "definitions": {
        "setVlanParameters": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string"
                },
                "vlanIds": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "pattern": "(^\\d{0,4}|^\\d{0,4}-d{0,4})+(,\\d{0,4}-\\d{0,4}|,\\d{0,4})*"
                    }
                },
                "mode": {
                    "enum": [
                        "Access",
                        "Trunk"
                    ],
                    "type": "string"
                }
            },
            "required": [
                "type", "vlanIds", "mode"
            ]
        },
        "removeVlanAction": {
            "allOf": [
                {
                    "$ref": "memory:definitions/action"
                },
                {
                    "properties": {
                        "connectionId": {
                            "type": "string"
                        },
                        "connectorAttributes": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/connectorAttribute"
                            }
                        }
                    },
                    "required": [
                        "connectionId",
                        "connectorAttributes"
                    ]
                }
            ]
        },
        "removeVlanResult": {
            "allOf": [
                {
                    "$ref": "memory:definitions/actionResponse"
                },
                {
                    "properties": {
                        "updatedInterface": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "updatedInterface"
                    ]
                }
            ]
        },

        "setVlanAction": {
            "allOf": [
                {
                    "$ref": "memory:definitions/action"
                },
                {
                    "properties": {
                        "connectionId": {
                            "type": "string"
                        },
                        "connectionParams": {
                            "$ref": "#/definitions/setVlanParameters"
                        },
                        "connectorAttributes": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/connectorAttribute"
                            }
                        }
                    },
                    "required": [
                        "connectionId",
                        "connectionParams",
                        "connectorAttributes"
                    ]
                }
            ]
        },
        "setVlanResult": {
            "allOf": [
                {
                    "$ref": "#/definitions/actionResult"
                },
                {
                    "properties": {
                        "updatedInterface": {
                            "type": "string"
                        }
                    },
                    "required": [

                        "updatedInterface"
                    ]
                }
            ]
        },
        "connectorAttribute": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string"
                },
                "attributeName": {
                    "type": "string"
                },
                "attributeValue": {
                    "type": "string"
                }
            },
            "required": [
                "attributeName",
                "attributeValue"
            ]
        }
    },
    "type": "object",
    "properties": {
        "driverRequest": {
            "type": "object",
            "properties": {
                "actions": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"$ref": "memory:definitions/setVlanAction"},
                            {"$ref": "memory:definitions/removeVlanAction"}
                        ]
                    }
                }
            }
        },
        "driverResponse": {
            "type": "object",
            "properties": {
                "actionResults": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"$ref": "#/definitions/setVlanResult"},
                            {"$ref": "#/definitions/removeVlanResult"}
                        ]
                    }
                }
            }
        }
    }
}

BASE_SCHEMA = {
    #"$schema": "base_schema.json",
    "definitions": {
        "actionTarget": {
            "type": "object",
            "properties": {
                "fullName": {
                    "type": "string"
                },
                "fullAddress": {
                    "type": "string"
                }
            },
            "required": [
                "fullName", "fullAddress"
            ]
        },
        "action": {
            "type": "object",
            "properties": {
                "actionId": {
                    "type": "string"
                },
                "type": {
                    "type": "string"
                },
                "actionTarget": {
                    "$ref": "#/definitions/actionTarget"
                }
            },
            "required": [
                "actionId",
                "type",
                "actionTarget"
            ]
        },
        "actionResult": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string"
                },
                "actionId": {
                    "type": "string"
                },
                "infoMessage": {
                    "type": "string"
                },
                "errorMessage": {
                    "type": "string"
                },
                "success": {
                    "type": "boolean"
                }
            },
            "required": [
                "actionId",
                "type",
                "infoMessage",
                "errorMessage",
                "success"
            ]
        }

    },
    "type": "object",
    "properties": {
        "driverRequest": {
            "type": "object",
            "properties": {
                "actions": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/action"
                    }
                }
            }
        },
        "driverResponse": {
            "type": "object",
            "properties": {
                "actionResults": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/actionResult"
                    }
                }
            }
        }
    }
}
