"""
ai_summarizer.py
Optional GenAI layer: given an error log line, asks an LLM (via Groq)
for a plausible root cause and next debugging step. Maps directly to
the job's "Good to have: Generative AI" skill.

If no API key is configured, explain_error() returns a clear message
instead of raising, so the rest of the app keeps working without it.
"""

import os

from groq import Groq

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = (
    "You are an application support engineer assistant. Given a single "
    "log line from a production system, respond in at most 4 short bullet "
    "points: (1) likely root cause, (2) which component is probably "
    "involved, (3) one concrete next debugging step, (4) severity if it "
    "were left unresolved. Be concise and practical, no preamble."
)


def explain_error(log_message: str, api_key: str | None = None) -> str:
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        return (
            "AI explanation unavailable: no GROQ_API_KEY configured. "
            "Add one in the sidebar or as an environment variable/Streamlit secret."
        )

    try:
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Log line: {log_message}"},
            ],
            temperature=0.3,
            max_tokens=250,
        )
        return response.choices[0].message.content
    except Exception as exc:  # network/auth/model errors shouldn't crash the UI
        return f"AI explanation failed: {exc}"
