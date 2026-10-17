"""Gemma 4 safety guard: a phrased summary is rejected if it introduces any number
that is not in the deterministic tool answer. Uses a fake client (no network)."""
from types import SimpleNamespace
from copilot import gemma, agent


class _Fake:
    def __init__(self, reply): self.reply, self.models = reply, []
    @property
    def chat(self): return SimpleNamespace(completions=SimpleNamespace(create=self._create))
    def _create(self, model, timeout, messages):
        self.models.append(model)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.reply))])


ANSWER = "WELL-0001: 4 rule breach(es), USD 5,000 in fines open. SR-02: contained after about 7 h vs 4 h limit (MNT-0001-029)."


def test_summary_with_only_tool_numbers_is_accepted(monkeypatch):
    fake = _Fake("WELL-0001 has 4 breaches and USD 5,000 open; one spill took about 7 h to contain.")
    monkeypatch.setattr(gemma, "_client", lambda: (fake, "gemma-4-31b-it"))
    r = gemma.phrase("Which rules has WELL-0001 broken?", ANSWER)
    assert r["ok"] and r["summary"] and r["rejected_numbers"] == [] and r["model"] == "gemma-4-31b-it"


def test_summary_inventing_a_number_is_rejected(monkeypatch):
    fake = _Fake("WELL-0001 took about 1.7 h to contain and owes USD 5,000.")
    monkeypatch.setattr(gemma, "_client", lambda: (fake, "gemma-4-31b-it"))
    r = gemma.phrase("Which rules has WELL-0001 broken?", ANSWER)
    assert not r["ok"] and r["summary"] is None and "1.7" in r["rejected_numbers"]


def test_gemma4_is_default_and_has_open_weight_fallback(monkeypatch):
    for k in ("GEMINI_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "XAI_API_KEY", "GROQ_API_KEY", "AIC_LLM_BASE", "AIC_LLM_MODEL", "AIC_LLM_PROVIDER"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    assert agent.llm_config()[2] == "gemma-4-31b-it"
    assert gemma._gemma_models("gemma-4-31b-it") == ["gemma-4-31b-it", "gemma-4-26b-a4b-it"]
    monkeypatch.delenv("GEMINI_API_KEY"); monkeypatch.setenv("AIC_LLM_BASE", "http://localhost:11434/v1")
    assert agent.llm_config()[2].startswith("gemma4")


def test_no_key_means_no_llm_call(monkeypatch):
    monkeypatch.setattr(gemma, "_client", lambda: (None, None))
    assert gemma.phrase("q", ANSWER) == {"ok": False, "reason": "no LLM key"}
