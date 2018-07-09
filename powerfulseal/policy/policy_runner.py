# Copyright 2017 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import random
import time
from jsonschema import validate
import yaml
import pkgutil
import logging
from .pod_scenario import PodScenario
from .node_scenario import NodeScenario

logger = logging.getLogger(__name__)


class PolicyRunner():
    """ Reads, validates and executes a JSON schema-compliant policy
    """

    @classmethod
    def get_schema(cls):
        """ Reads the schema from the file
        """
        data = {
            "title": "PowerfulSeal config",
            "type": "object",
            "properties": {
                "config": {
                    "type": "object",
                    "$ref": "#/definitions/config"
                },
                "nodeScenarios": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "$ref": "#/definitions/nodeScenario"
                    }
                },
                "podScenarios": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "$ref": "#/definitions/podScenario"
                    }
                }
            },
            "definitions": {

                "config": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "minSecondsBetweenRuns": {
                            "type": "number"
                        },
                        "maxSecondsBetweenRuns": {
                            "type": "number"
                        }
                    },
                    "required": ["minSecondsBetweenRuns"]
                },

                "nodeScenario": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "match": {
                            "type": "array",
                            "items": {
                                "oneOf": [
                                    {"$ref": "#/definitions/filterPropertyNode"}
                                ]
                            }
                        },
                        "filters": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "oneOf": [
                                    {"$ref": "#/definitions/filterPropertyNode"},
                                    {"$ref": "#/definitions/filterDayTime"},
                                    {"$ref": "#/definitions/filterRandomSample"},
                                    {"$ref": "#/definitions/filterProbability"}
                                ]
                            }
                        },
                        "actions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "oneOf": [
                                    {"$ref": "#/definitions/actionStartNode"},
                                    {"$ref": "#/definitions/actionStopNode"},
                                    {"$ref": "#/definitions/actionExecuteNode"},
                                    {"$ref": "#/definitions/actionWait"}
                                ]
                            }
                        }
                    },
                    "required": ["name", "match", "filters", "actions"]
                },

                "filterRandomSample": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "randomSample": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "size": {
                                    "type": "number"
                                },
                                "ratio": {
                                    "type": "number"
                                }
                            }
                        }
                    },
                    "required": ["randomSample"]
                },

                "filterProbability": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "probability": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "probabilityPassAll": {
                                    "type": "number"
                                }
                            },
                            "required": ["probabilityPassAll"]
                        }
                    },
                    "required": ["probability"]
                },

                "time": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "hour": {
                            "type": "number"
                        },
                        "minute": {
                            "type": "number"
                        },
                        "second": {
                            "type": "number"
                        }
                    },
                    "required": ["hour", "minute", "second"]
                },

                "filterDayTime": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "dayTime": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "onlyDays": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "monday",
                                            "tuesday",
                                            "wednesday",
                                            "thursday",
                                            "friday",
                                            "saturday",
                                            "sunday"
                                        ]
                                    }
                                },
                                "startTime": {
                                    "type": "object",
                                    "$ref": "#/definitions/time"
                                },
                                "endTime": {
                                    "type": "object",
                                    "$ref": "#/definitions/time"
                                }
                            },
                            "required": ["onlyDays", "startTime", "endTime"]
                        }
                    },
                    "required": ["dayTime"]
                },

                "filterPropertyNode": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "property": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "enum": [
                                        "name",
                                        "ip",
                                        "group",
                                        "az",
                                        "state"
                                    ]
                                },
                                "value": {
                                    "type": "string"
                                }
                            },
                            "required": ["name", "value"]
                        }
                    },
                    "required": ["property"]
                },

                "actionStartNode": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "start": {
                            "type": ["object", "null"],
                            "additionalProperties": False
                        }
                    },
                    "required": ["start"]
                },

                "actionStopNode": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "stop": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "force": {
                                    "type": "boolean"
                                }
                            }
                        }
                    },
                    "required": ["stop"]
                },

                "actionExecuteNode": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "execute": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "cmd": {
                                    "type": "string"
                                }
                            },
                            "required": ["cmd"]
                        }
                    },
                    "required": ["execute"]
                },

                "actionWait": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "wait": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "seconds": {
                                    "type": "number"
                                }
                            },
                            "required": ["seconds"]
                        }
                    },
                    "required": ["wait"]
                },

                "podScenario": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "match": {
                            "type": "array",
                            "items": {
                                "oneOf": [
                                    {"$ref": "#/definitions/matchPodNamespace"},
                                    {"$ref": "#/definitions/matchPodDeploymentAndNamespace"},
                                    {"$ref": "#/definitions/matchPodLabelsAndNamespace"}
                                ]
                            }
                        },
                        "filters": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "oneOf": [
                                    {"$ref": "#/definitions/filterPropertyPod"},
                                    {"$ref": "#/definitions/filterDayTime"},
                                    {"$ref": "#/definitions/filterRandomSample"},
                                    {"$ref": "#/definitions/filterProbability"}
                                ]
                            }
                        },
                        "actions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "oneOf": [
                                    {"$ref": "#/definitions/actionKillPod"},
                                    {"$ref": "#/definitions/actionWait"}
                                ]
                            }
                        }
                    },
                    "required": ["name", "match", "filters", "actions"]
                },

                "matchPodNamespace": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "namespace": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "name": {
                                    "type": "string"
                                }
                            },
                            "required": ["name"]
                        }
                    },
                    "required": ["namespace"]
                },

                "matchPodDeploymentAndNamespace": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "deployment": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "name": {
                                    "type": "string"
                                },
                                "namespace": {
                                    "type": "string"
                                }
                            },
                            "required": ["name", "namespace"]
                        }
                    },
                    "required": ["deployment"]
                },

                "matchPodLabelsAndNamespace": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "labels": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "selector": {
                                    "type": "string"
                                },
                                "namespace": {
                                    "type": "string"
                                }
                            },
                            "required": ["selector", "namespace"]
                        }
                    },
                    "required": ["labels"]
                },

                "filterPropertyPod": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "property": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "enum": [
                                        "name",
                                        "state"
                                    ]
                                },
                                "value": {
                                    "type": "string"
                                }
                            },
                            "required": ["name", "value"]
                        }
                    },
                    "required": ["property"]
                },

                "actionKillPod": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "kill": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "probability": {
                                    "type": "number"
                                },
                                "force": {
                                    "type": "boolean"
                                }
                            }
                        }
                    },
                    "required": ["kill"]
                }
            }
        }

        return data

    @classmethod
    def validate_file(cls, filename, schema=None):
        """ Validates a policy against the JSON schema
        """
        schema = schema or cls.get_schema()
        with open(filename, "r") as f:
            policy = yaml.load(f.read())
        validate(policy, schema)
        return policy

    @classmethod
    def run(cls, policy, inventory, k8s_inventory, driver, executor, loops=None):
        """ Runs a policy forever
        """
        config = policy.get("config", {})
        wait_min = config.get("minSecondsBetweenRuns", 0)
        wait_max = config.get("maxSecondsBetweenRuns", 300)
        node_scenarios = [
            NodeScenario(
                name=item.get("name"),
                schema=item,
                inventory=inventory,
                driver=driver,
                executor=executor,
            )
            for item in policy.get("nodeScenarios", [])
        ]
        pod_scenarios = [
            PodScenario(
                name=item.get("name"),
                schema=item,
                inventory=inventory,
                k8s_inventory=k8s_inventory,
                executor=executor,
            )
            for item in policy.get("podScenarios", [])
        ]
        while loops is None or loops > 0:
            for scenario in node_scenarios:
                scenario.execute()
            for scenario in pod_scenarios:
                scenario.execute()
            sleep_time = int(random.uniform(wait_min, wait_max))
            logger.info("Sleeping for %s seconds", sleep_time)
            time.sleep(sleep_time)
            inventory.sync()
            if loops is not None:
                loops -= 1
        return node_scenarios, pod_scenarios
