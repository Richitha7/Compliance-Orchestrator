import argparse
import asyncio
import json
import time
import requests
import websockets

SERVER_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/connect"

async def run_client(session_id: str, question: str, autoplay: bool, hitl: int, force_timeout: bool):
    # Step 1: Ask question via REST API
    ask_payload = {"session_id": session_id, "question": question}
    resp = requests.post(f"{SERVER_URL}/ask", json=ask_payload)
    resp.raise_for_status()
    job_id = resp.json()["job_id"]
    print(f"[client] Asked question: {question}")
    print(f"[client] Job ID: {job_id}")

    # Step 2: WebSocket connection (for demo, just connect)
    async with websockets.connect(f"{WS_URL}?session_id={session_id}") as ws:
        print(f"[client] Connected to {WS_URL}?session_id={session_id}")

        # Step 3: Poll results
        interactions_done = 0
        while True:
            result = requests.get(f"{SERVER_URL}/result", params={"job_id": job_id}).json()
            status = result.get("status")
            decision = result.get("decision")

            if decision:  # Final decision reached
                print("\n=== FINAL DECISION ===")
                print(json.dumps(result, indent=2))
                break

            # Handle HITL interruptions if required
            open_qs = result.get("open_questions", [])
            if open_qs and interactions_done < hitl and not force_timeout:
                q = open_qs[0]
                if "clarification" in q.lower():
                    payload = {
                        "job_id": job_id,
                        "action": "clarification",
                        "message": "MFA uses TOTP with 30s expiry."
                    }
                    requests.post(f"{SERVER_URL}/hitl", json=payload)
                    print("[client] Sent HITL clarification.")
                elif "screenshot" in q.lower() or "upload" in q.lower():
                    payload = {
                        "job_id": job_id,
                        "action": "upload",
                        "message": "Uploaded MFA config screenshot."
                    }
                    requests.post(f"{SERVER_URL}/hitl", json=payload)
                    print("[client] Sent HITL upload.")
                interactions_done += 1

            if force_timeout:
                print("[client] Simulating no HITL response (timeout)...")
                time.sleep(3)
                # Eventually server will fall back to insufficient_evidence
                pass

            time.sleep(2)  # Wait before polling again


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True, help="Session ID")
    ap.add_argument("--question", required=True, help="Question to ask")
    ap.add_argument("--autoplay", action="store_true", help="Automatically run until decision")
    ap.add_argument("--hitl", type=int, default=0, help="Number of HITL interruptions to simulate")
    ap.add_argument("--force-timeout", action="store_true", help="Simulate timeout (no HITL responses)")
    args = ap.parse_args()

    asyncio.run(run_client(args.session, args.question, args.autoplay, args.hitl, args.force_timeout))
