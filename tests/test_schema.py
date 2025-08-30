import json
from server.utils.guardrails import validate_decision

def test_schema():
    valid = validate_decision({
        "decision": "compliant",
        "confidence": 0.9,
        "risk_score": 0.1,
        "rationale": "ok",
        "citations": [{"doc_id":"d","chunk_id":"c","snippet":"s"}],
        "open_questions": [],
        "human_interactions": []
    })
    assert valid.decision == "compliant"

    invalid = validate_decision({"foo": "bar"})
    assert invalid.decision == "insufficient_evidence"
