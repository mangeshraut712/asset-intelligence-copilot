"""Gemma 4 (open-weight) helpers: answer phrasing with a number-preservation check, and multimodal photo description."""
import base64, os, re
from .agent import llm_config

def _client():
    cfg = llm_config()
    if not cfg: return None, None
    from openai import OpenAI
    k, base, model = cfg
    return OpenAI(api_key=k, base_url=base, max_retries=0), model

NUM = re.compile(r"\d+(?:[.,]\d+)*")

def _gemma_models(model):
    alt = {"google/gemma-4-31b-it:free": "google/gemma-4-26b-a4b-it:free", "gemma-4-31b-it": "gemma-4-26b-a4b-it"}.get(model)
    return [model] + ([alt] if alt else [])

def _chat(cl, model, messages, timeout):
    err = None
    for m in _gemma_models(model) * 2:   # each Gemma variant gets two tries (free endpoints return transient 5xx)
        try: return cl.chat.completions.create(model=m, timeout=timeout, messages=messages), m
        except Exception as e: err = e
    raise err

def phrase(question, answer_text):
    """Ask Gemma 4 for a 1-2 sentence operator-friendly summary. Rejected if it introduces any number not in the tool answer."""
    cl, model = _client()
    if not cl: return {"ok": False, "reason": "no LLM key"}
    r, model = _chat(cl, model, timeout=float(os.environ.get("AIC_PHRASE_TIMEOUT", 60)), messages=[
        {"role": "system", "content": "Summarise the copilot answer for a field operator in at most 2 sentences. Use ONLY facts and numbers that appear in the answer. Keep well IDs and record IDs exact. No new numbers."},
        {"role": "user", "content": f"Question: {question}\n\nCopilot answer (computed by deterministic tools):\n{answer_text[:3500]}"}])
    s = (r.choices[0].message.content or "").strip()
    src = set(n.replace(",", "") for n in NUM.findall(answer_text)) | set(NUM.findall(question))
    bad = [n for n in NUM.findall(s) if n.replace(",", "") not in src]
    return {"ok": not bad, "summary": s if not bad else None, "rejected_numbers": bad, "model": model}

def describe_image(data: bytes, mime: str, context: str = ""):
    """Multimodal: Gemma 4 describes an inspection photo. Advisory only; never overrides recorded data."""
    cl, model = _client()
    if not cl: return {"ok": False, "reason": "no LLM key"}
    url = f"data:{mime};base64,{base64.b64encode(data).decode()}"
    r, model = _chat(cl, model, timeout=90, messages=[{"role": "user", "content": [
        {"type": "text", "text": "You assist oil-field inspectors. Describe this well-pad photo in 3 short bullet points: visible equipment (pump jack, wellhead, flowline), any dark staining or pooled fluid that could be a crude spill (estimate % of pad if visible), and anything abnormal. Say clearly if unsure. " + context},
        {"type": "image_url", "image_url": {"url": url}}]}])
    return {"ok": True, "description": r.choices[0].message.content, "model": model}
