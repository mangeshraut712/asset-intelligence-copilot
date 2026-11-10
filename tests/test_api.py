from fastapi.testclient import TestClient
from copilot.server import app
c = TestClient(app)

def test_api(fresh):
    assert c.get("/").status_code == 200 and len(c.get("/api/users").json()) >= 10
    r = c.post("/api/ask", json={"question": "Show a heatmap of 2026 spills by geographic area and month.", "user": "U-401"}).json()
    assert r["visual"]["type"] == "heatmap" and r["citations"]
    assert c.get("/api/healthz").json()["ok"]


def test_vision_rejects_oversized_upload_before_calling_the_model(monkeypatch):
    from copilot import gemma, server
    called = []
    monkeypatch.setattr(gemma, "describe_image", lambda *a, **k: called.append(a) or {"ok": True})
    big = b"\xff" * (server.MAX_IMAGE_BYTES + 10)
    r = c.post("/api/vision", files={"file": ("big.jpg", big, "image/jpeg")}).json()
    assert r == {"ok": False, "reason": "image too large (max 6 MB)"}
    assert called == []
    ok = c.post("/api/vision", files={"file": ("small.jpg", b"\xff\xd8\xff", "image/jpeg")}).json()
    assert ok["ok"] is True and len(called) == 1
