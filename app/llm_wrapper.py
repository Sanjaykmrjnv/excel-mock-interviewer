import os
from pyexpat.errors import messages
from typing import Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

genai_api_key = os.getenv("GENAI_API_KEY")

client = genai.Client(genai_api_key=genai_api_key)

def llm_evaluate_stub(kind: str, payload: Any) -> Dict[str, Any]:
    """
    Simple deterministic stub for PoC that returns
    a numeric score and short feedback.
    """
    if kind == "concept":
        text = str(payload).lower()
        if "$a$1" in text or "absolute" in text:
            return {"score": 4, "explanation": "Good — you mentioned absolute referencing."}
        return {"score": 2, "explanation": "Partial answer. Mention absolute vs relative referencing."}

    # workbook kind
    if isinstance(payload, dict) and payload.get("pass"):
        return {"score": 5, "explanation": "Workbook checks passed."}
    else:
        return {"score": 1, "explanation": "Workbook mismatches found. Check formulas."}

def llm_evaluate(kind: str, payload: Any) -> Dict[str, Any]:
    """
    If API_KEY present - call Chat Completions, else fallback to stub.
    (This function keeps the place to swap real LLM calls in.)
    """
    if genai_api_key is None:
        return llm_evaluate_stub(kind, payload)

    # Minimal Google GenAI usage example.
    try:
        system = "You are an expert Excel grader. Provide a JSON with 'score' (0-5) and 'explanation'. Keep output compact."
        user = f"Kind: {kind}\nPayload: {payload}"
        resp = client.models.generate_content(
            model="gemini-2.5-flash-lite",  # change to your available model
            contents=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=200,
            temperature=0
        )
        text = resp["choices"][0]["message"]["content"].strip()
        # Expect a small JSON back. Try parse; fallback to stub.
        import json
        try:
            return json.loads(text)
        except Exception:
            return {"score": 3, "explanation": text}
    except Exception:
        return llm_evaluate_stub(kind, payload)
