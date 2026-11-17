import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "payload",
    [
        {"recipient": "X", "zip_code": "3030", "weight_kg": 0},
        {"recipient": "X", "zip_code": "3030", "weight_kg": -1},
        {"recipient": "X", "zip_code": "3030", "weight_kg": 30.5},
        {"recipient": "X", "zip_code": "303", "weight_kg": 1},
        {"recipient": "X", "zip_code": "30301", "weight_kg": 1},
        {"recipient": "X", "zip_code": "30a0", "weight_kg": 1},
    ],
)
def test_invalid_input_is_rejected_with_422(payload):
    assert client.post("/parcels", json=payload).status_code == 422


def test_valid_input_still_accepted():
    res = client.post("/parcels", json={"recipient": "X", "zip_code": "1201", "weight_kg": 5})
    assert res.status_code == 201
