from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_get_parcel():
    created = client.post(
        "/parcels", json={"recipient": "Anna Muster", "zip_code": "3030", "weight_kg": 1.0}
    )
    assert created.status_code == 201
    body = created.json()
    assert body["price_chf"] == 7.00
    assert body["status"] == "registered"

    fetched = client.get(f"/parcels/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["recipient"] == "Anna Muster"


def test_unknown_parcel_returns_404():
    assert client.get("/parcels/99999").status_code == 404


def test_mid_tier_price():
    created = client.post(
        "/parcels", json={"recipient": "Ben", "zip_code": "8001", "weight_kg": 5.0}
    )
    assert created.json()["price_chf"] == 9.70
