import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_search_by_location_returns_results(client):
    resp = client.post("/search/doctors", json={"location": "Bucharest"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    assert all(r["location"] == "Bucharest" for r in data["results"])


def test_fuzzy_location_typo_resolves(client):
    resp = client.post("/search/doctors", json={"location": "Bukalest"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    assert all(r["location"] == "Bucharest" for r in data["results"])


def test_missing_search_fields_returns_422(client):
    resp = client.post("/search/doctors", json={"language": "English"})
    assert resp.status_code == 422


def test_language_filter_applied(client):
    resp = client.post("/search/doctors", json={"location": "Bucharest", "language": "English"})
    assert resp.status_code == 200
    assert all("English" in r["languages"] for r in resp.json()["results"])


def test_unrecognized_location_returns_empty(client):
    resp = client.post("/search/doctors", json={"location": "ZZZZZZZ"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_result_shape(client):
    resp = client.post("/search/doctors", json={"specialty": "Cardiology"})
    assert resp.status_code == 200
    r = resp.json()["results"][0]
    for field in ["doctor", "clinic", "speciality", "location", "availability",
                  "languages", "rating", "phone", "email", "match_score"]:
        assert field in r


def test_max_10_results_returned(client):
    resp = client.post("/search/doctors", json={"location": "Bucharest"})
    assert resp.json()["total"] <= 10
