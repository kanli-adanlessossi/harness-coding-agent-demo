import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_saturday_delivery_adds_surcharge():
    res = client.post(
        "/parcels",
        json={"recipient": "Lea", "zip_code": "6003", "weight_kg": 1.0, "saturday_delivery": True},
    )
    assert res.status_code == 201
    assert res.json()["price_chf"] == pytest.approx(11.80)


def test_saturday_delivery_defaults_to_false():
    res = client.post("/parcels", json={"recipient": "Lea", "zip_code": "6003", "weight_kg": 1.0})
    assert res.status_code == 201
    assert res.json()["price_chf"] == pytest.approx(7.00)
    assert res.json()["saturday_delivery"] is False
