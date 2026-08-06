from fastapi.testclient import TestClient

from agent.app import app

client = TestClient(app)


def test_root_health_check():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_by_emotion_rejects_invalid_emotion():
    resp = client.get("/api/memes/by-emotion", params={"emotion": "invalid"})
    assert resp.status_code == 400
