from pydantic import BaseModel


class ParcelIn(BaseModel):
    recipient: str
    zip_code: str
    weight_kg: float


class Parcel(ParcelIn):
    id: int
    status: str = "registered"
    price_chf: float
