from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert data["app"] == "LegalEase"


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_generate_demo_mode():

    payload = {
        "document_type": "NDA",

        "parties": (
            "Alice (Disclosing Party), "
            "Beta Ltd (Receiving Party)"
        ),

        "terms": (
            "Confidential information must be protected; "
            "Term is two years"
        ),

        "effective_date": "September 29, 2026",
    }

    response = client.post(
        "/generate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert "document" in data

    assert "NDA" in data["document"]

    assert (
        "Confidential information"
        in data["document"]
    )