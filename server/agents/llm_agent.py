# server/agents/llm_agent.py
import os
from typing import Dict

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  


async def llm_agent(question: str, context: str = "") -> Dict:
    """
    Simple LLM agent. If OPENAI_API_KEY is set and openai library is available,
    it asks the model; otherwise returns a safe fallback string.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key or OpenAI is None:
        return {"answer": "LLM agent not configured (missing OPENAI_API_KEY or openai library)."}

    try:
        client = OpenAI(api_key=api_key)

        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # small/cheap + reasoning ability
            messages=[
                {"role": "system", "content": "You are a compliance AI assistant. Be concise and cite evidence if provided."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
            ],
            temperature=0.2,
            max_tokens=300,
        )
        answer = resp.choices[0].message.content.strip()
        return {"answer": answer}

    except Exception as e:
        return {"answer": f"LLM error: {e}"}
