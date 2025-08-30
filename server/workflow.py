from __future__ import annotations
import asyncio, uuid, time
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential_jitter
from .agents.policy_retriever import PolicyRetriever
from .agents.evidence_collector import EvidenceCollector
from .agents.vision_ocr import VisionOCR
from .agents.code_scanner import CodeScanner
from .agents.risk_scorer import RiskScorer
from .agents.red_team_critic import RedTeamCritic
from .agents.aggregator import aggregate
from .utils.config import settings
from .utils.logging import log
from .storage.mongo import store

@retry(stop=stop_after_attempt(2), wait=wait_exponential_jitter())
async def run_job(question: str, session_id: str, ws_send, artifact_path: Optional[str] = None, code_snippets: Optional[list[str]] = None):
    await store.append_history(session_id, {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "event": "planner_started", "data": {}})
    await ws_send({"type": "progress_update", "stage": "planner_started", "status": "ok", "meta": {}})

    # Fan-out: run collectors in parallel
    policy = PolicyRetriever()
    evidence = EvidenceCollector()
    vision = VisionOCR()
    code = CodeScanner()

    try:
        results = await asyncio.wait_for(asyncio.gather(
            policy.run(question=question),
            evidence.run(question=question),
            vision.run(image_path=artifact_path),
            code.run(code_snippets=code_snippets),
        ), timeout=settings.TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        # HITL approval to proceed with reduced evidence
        rid = str(uuid.uuid4())
        prompt = "Timeout while collecting evidence. Approve proceed with reduced evidence?"
        await store.append_history(session_id, {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "event": "awaiting_human", "data": {"request_id": rid}})
        await ws_send({"type": "hitl_request", "payload": {"session_id": session_id, "request_id": rid, "type": "approval", "prompt": prompt}})
        # In real system, we'd await external response; here we proceed after short wait
        await asyncio.sleep(3)
        results = await asyncio.gather(
            policy.run(question=question),
            evidence.run(question=question),
            vision.run(image_path=artifact_path),
            code.run(code_snippets=code_snippets),
        )

    policy_res, evidence_res, vision_res, code_res = results
    await ws_send({"type": "progress_update", "stage": "parallel_merge", "status": "ok", "meta": {}})

    risk = await RiskScorer().run(policy=policy_res.data, evidence=evidence_res.data, vision=vision_res.data, code=code_res.data)
    critic = await RedTeamCritic().run({"policy": policy_res.data, "evidence": evidence_res.data, "vision": vision_res.data, "code": code_res.data})
    await ws_send({"type": "progress_update", "stage": "critic_flags", "status": "ok", "meta": {"open_questions": critic.data.get("open_questions", [])}})

    # If critic demands missing items, trigger HITL
    if critic.data.get("open_questions"):
        rid = str(uuid.uuid4())
        await ws_send({"type": "hitl_request", "payload": {"session_id": session_id, "request_id": rid, "type": "upload_request", "prompt": "Upload MFA settings screenshot.", "required_artifact": "image"}})
        await store.append_history(session_id, {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "event": "awaiting_human", "data": {"request_id": rid, "type": "upload_request"}})
        # For demo: we wait briefly to simulate resume (real system would wait for /hitl or WS response)
        await asyncio.sleep(2)

    final = aggregate(policy_res, evidence_res, vision_res, code_res, risk, critic)
    await ws_send({"type": "progress_update", "stage": "finalized", "status": "ok", "meta": {"decision": final["decision"]}})
    return final
