from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_triage_returns_suggestions():
    response = client.post("/triage", json={
        "text": "Water pipe leaking outside the school",
        "channel": "web_portal",
        "location": "Ward 4"
    })
    assert response.status_code == 200
    body = response.json()
    assert "routing_suggestion" in body
    assert "duplicate_candidates" in body
    assert "safety_review" in body


def test_route_review_requires_department():
    # C-001 is part of the synthetic seed data.
    response = client.post("/review/C-001", json={
        "action": "confirm_route",
        "staff_id": "demo-staff",
        "reason": "Confirmed after checking the complaint",
    })
    assert response.status_code == 422


def test_review_is_audited():
    response = client.post("/review/C-001", json={
        "action": "confirm_route",
        "staff_id": "demo-staff",
        "reason": "Confirmed after checking the complaint",
        "selected_department": "Water",
    })
    assert response.status_code == 200
    assert response.json()["recorded"] is True
    audit = client.get("/audit").json()
    assert audit["count"] >= 1
