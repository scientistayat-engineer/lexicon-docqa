import json
import re
import time

from app.config import settings
from app.prompts.templates import build_messages


class LLMError(RuntimeError):
    pass


def _client():
    if not settings.groq_api_key:
        raise LLMError("GROQ_API_KEY is not set. Add it to .env or your Vercel environment variables.")
    from groq import Groq
    return Groq(api_key=settings.groq_api_key)


def _call(**kwargs):
    """Call Groq and wait/retry when the tokens-per-minute limit is hit."""
    client = _client()
    for attempt in range(8):
        try:
            return client.chat.completions.create(**kwargs)
        except Exception as e:
            msg = str(e)
            if "429" not in msg and "rate_limit" not in msg:
                raise LLMError(f"Groq request failed: {msg}")
            m = re.search(r"try again in (?:(\d+)m)?([\d.]+)s", msg)
            wait = (int(m.group(1) or 0) * 60 + float(m.group(2)) + 0.5) if m else 5 * (attempt + 1)
            time.sleep(wait)
    raise LLMError("Groq rate limit is still exceeded after several retries. Wait a minute and try again.")


def answer(mode: str, question: str, chunks: list[dict]) -> str:
    r = _call(model=settings.groq_model, temperature=0.2, messages=build_messages(mode, question, chunks))
    return r.choices[0].message.content.strip()


def judge(question: str, chunks: list[dict], ans: str) -> dict:
    """LLM-as-judge: scores accuracy, clarity and relevance from 1 to 10."""
    prompt = ("Rate this answer from 1 to 10 for accuracy (supported by the context), clarity and "
              'relevance. Reply as JSON: {"accuracy":n,"clarity":n,"relevance":n}\n\n'
              f"Context: {' '.join(c['text'] for c in chunks)}\n\nQuestion: {question}\n\nAnswer: {ans}")
    try:
        r = _call(model=settings.groq_model, temperature=0, response_format={"type": "json_object"},
                  messages=[{"role": "user", "content": prompt}])
        raw = json.loads(r.choices[0].message.content)
        s = {k: float(raw[k]) for k in ("accuracy", "clarity", "relevance")}
    except LLMError:
        raise
    except Exception:
        s = {"accuracy": 0.0, "clarity": 0.0, "relevance": 0.0}
    s["avg"] = round((s["accuracy"] + s["clarity"] + s["relevance"]) / 3, 1)
    return s