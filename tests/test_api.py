from fastapi.testclient import TestClient
from copilot.server import app
c = TestClient(app)

def test_api(fresh):
    assert c.get("/").status_code == 200 and len(c.get("/api/users").json()) >= 10
    r = c.post("/api/ask", json={"question": "Show a heatmap of 2026 spills by geographic area and month.", "user": "U-401"}).json()
    assert r["visual"]["type"] == "heatmap" and r["citations"]
    assert c.get("/api/healthz").json()["ok"]
