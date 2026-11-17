from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_status_of_existing_parcel():
    created = client.post("/parcels", json={"recipient": "Eva", "zip_code": "3000", "weight_kg": 1.0}).json()
    res = client.get(f"/parcels/{created['id']}/status")
    assert res.status_code == 200
    assert res.json() == {"id": created["id"], "status": "registered"}


def test_status_of_unknown_parcel_is_404_with_detail():
    res = client.get("/parcels/424242/status")
    assert res.status_code == 404
    assert res.json() == {"detail": "Parcel not found"}
