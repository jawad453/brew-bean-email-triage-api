import os

os.environ["AUTH_TOKEN"] = "test-token"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_triage_requires_authentication():
    response = client.post(
        "/triage",
        json={
            "email_text": "I want to know the status of my order."
        },
    )

    assert response.status_code == 401


def test_triage_with_valid_token():
    response = client.post(
        "/triage",
        headers={"X-Auth-Token": "test-token"},
        json={
            "email_text": "I want to know the status of my order."
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert "category" in result
    assert "confidence" in result
    assert result["category"] == "order"
    assert 0.0 <= result["confidence"] <= 1.0


def test_invalid_token():
    response = client.post(
        "/triage",
        headers={"X-Auth-Token": "wrong-token"},
        json={
            "email_text": "Your coffee was excellent."
        },
    )

    assert response.status_code == 401


def test_low_confidence_empty_email():
    response = client.post(
        "/triage",
        headers={"X-Auth-Token": "test-token"},
        json={
            "email_text": ""
        },
    )

    assert response.status_code == 200
    assert response.json()["category"] == "Uncertain"