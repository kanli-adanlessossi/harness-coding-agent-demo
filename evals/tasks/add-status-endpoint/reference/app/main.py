from fastapi import FastAPI, HTTPException

from .models import Parcel, ParcelIn
from .store import store
from .tariff import price_chf

app = FastAPI(title="Parcel Service (demo)")


@app.post("/parcels", status_code=201, response_model=Parcel)
def create_parcel(parcel: ParcelIn) -> Parcel:
    return store.add(parcel, price_chf(parcel.weight_kg))


@app.get("/parcels/{parcel_id}", response_model=Parcel)
def get_parcel(parcel_id: int) -> Parcel:
    parcel = store.get(parcel_id)
    if parcel is None:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel


@app.get("/parcels/{parcel_id}/status")
def get_parcel_status(parcel_id: int) -> dict:
    parcel = get_parcel(parcel_id)
    return {"id": parcel.id, "status": parcel.status}
