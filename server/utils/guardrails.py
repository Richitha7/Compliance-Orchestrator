from pydantic import ValidationError
from ..models import FinalDecision

SAFE_REFUSAL = {
    "decision": "insufficient_evidence",
    "confidence": 0.0,
    "risk_score": 0.0,
    "rationale": "Request is unsupported or unsafe for this system.",
    "citations": [],
    "open_questions": [],
    "human_interactions": []
}

def validate_decision(payload: dict) -> FinalDecision:
    try:
        return FinalDecision(**payload)
    except ValidationError as e:
        # Convert invalid to safe refusal
        return FinalDecision(**SAFE_REFUSAL)
