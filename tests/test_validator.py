from diagramm.validator import DiagramValidator


def test_validator_accepts_valid_payload():
    payload = {
        "diagram_type": "activity",
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "step", "type": "action", "label": "Шаг"},
            {"id": "end", "type": "end"},
        ],
        "edges": [
            {"from": "start", "to": "step"},
            {"from": "step", "to": "end"},
        ],
    }
    validator = DiagramValidator()
    result = validator.validate_payload(payload)
    assert result.valid


def test_validator_rejects_missing_start():
    payload = {
        "diagram_type": "activity",
        "nodes": [
            {"id": "step", "type": "action", "label": "Шаг"},
            {"id": "end", "type": "end"},
        ],
        "edges": [
            {"from": "step", "to": "end"},
        ],
    }
    validator = DiagramValidator()
    result = validator.validate_payload(payload)
    assert not result.valid
    assert any("start" in error for error in result.errors)
