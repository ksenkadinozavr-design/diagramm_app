LLM_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["diagram_type", "nodes", "edges"],
    "additionalProperties": False,
    "properties": {
        "diagram_type": {
            "type": "string",
            "enum": [
                "activity",
                "idef0",
                "idef1x",
                "idef3",
                "idef4",
                "idef5",
                "dfd",
                "uml_use_case",
                "uml_activity",
                "uml_class",
                "bpmn",
                "flowchart",
            ],
        },
        "nodes": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "type"],
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "type": {
                        "type": "string",
                        "enum": [
                            "start",
                            "end",
                            "action",
                            "decision",
                            "process",
                            "input",
                            "output",
                            "entity",
                            "store",
                            "actor",
                            "class",
                        ],
                    },
                    "label": {"type": "string"},
                },
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["from", "to"],
                "additionalProperties": False,
                "properties": {
                    "from": {"type": "string", "minLength": 1},
                    "to": {"type": "string", "minLength": 1},
                    "condition": {"type": "string"},
                },
            },
        },
    },
}
