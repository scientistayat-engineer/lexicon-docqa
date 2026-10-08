from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_invalid_mode():
    r = client.post("/api/ask", json={"question": "hi", "mode": "bogus"})
    assert r.status_code == 400
