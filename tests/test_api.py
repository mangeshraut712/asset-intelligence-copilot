from fastapi.testclient import TestClient
from copilot.server import app
c = TestClient(app)

def test_api(fresh):
    assert c.get("/").status_code == 200 and len(c.get("/api/users").json()) >= 10
    r = c.post("/api/ask", json={"question": "Show a heatmap of 2026 spills by geographic area and month.", "user": "U-401"}).json()
    assert r["visual"]["type"] == "heatmap" and r["citations"]
    assert c.get("/api/healthz").json()["ok"]


def test_missing_sample_is_404_not_500():
    r = TestClient(app, raise_server_exceptions=False).get("/samples/does-not-exist.jpg")
    assert r.status_code == 404
    assert c.get("/samples/inspection-WELL-0151.jpg").status_code == 200
