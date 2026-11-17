from pydantic import BaseModel


class ParcelIn(BaseModel):
    recipient: str
    zip_code: str
    weight_kg: float
    saturday_delivery: bool = False


class Parcel(ParcelIn):
    id: int
    status: str = "registered"
    price_chf: float
