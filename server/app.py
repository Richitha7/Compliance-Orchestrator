from __future__ import annotations
import os, uuid, asyncio, json, time
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import ORJSONResponse
from .models import AskRequest, AskResponse
from .utils.config import settings
from .utils.logging import log
from .storage.mongo import store
from .storage.vectorstore import vector_store
from .utils.guardrails import validate_decision
from .workflow import run_job

app = FastAPI(default_response_class=ORJSONResponse)

# In-memory job results for demo
JOB_RESULTS: Dict[str, Dict[str, Any]] = {}

@app.on_event("startup")
async def startup():
    await store.init()
    vector_store.load_model()
    # Seed tiny corpus for demo
    vector_store.add_documents([
        {"doc_id": "policy-001", "chunk_id": "c1", "text": "Policy X mandates MFA for all user logins."},
        {"doc_id": "policy-001", "chunk_id": "c2", "text": "Acceptable MFA methods include TOTP, SMS OTP, and push notifications."},
        {"doc_id": "org-std-01", "chunk_id": "c1", "text": "Org standard: mobile login must enforce TOTP with 30s window."},
        {"doc_id": "product-auth", "chunk_id": "c5", "text": "Our login service uses TOTP-based MFA after password verification."},
    ])

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    job_id = str(uuid.uuid4())

    async def ws_stub_send(msg: Dict[str, Any]):
        # For REST-only flows (no WS connected), just log.
        log.info("progress", **msg)

    # Start job in background task
    async def runner():
        final = await run_job(question=req.question, session_id=req.session_id, ws_send=ws_stub_send)
        JOB_RESULTS[job_id] = final

    asyncio.create_task(runner())
    return {"job_id": job_id}

@app.get("/result")
async def result(job_id: str = Query(...)):
    if job_id in JOB_RESULTS:
        return validate_decision(JOB_RESULTS[job_id]).model_dump()
    return {"status": "pending"}

@app.post("/hitl")
async def hitl():
    # For brevity, this demo uses WS for HITL and simulates resume automatically in workflow.
    return {"status": "ok"}

@app.get("/history")
async def history(session_id: str):
    return await store.get_history(session_id)

@app.websocket("/connect")
async def connect(ws: WebSocket, session_id: str):
    await ws.accept()
    try:
        async def ws_send(payload: Dict[str, Any]):
            await ws.send_json(payload)
        # Keep connection open for pushes; in a real system we'd associate session to ws
        while True:
            data = await ws.receive_text()
            await ws.send_text(f"echo:{data}")
    except WebSocketDisconnect:
        pass
