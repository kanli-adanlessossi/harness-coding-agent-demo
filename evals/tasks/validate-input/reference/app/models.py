from pydantic import BaseModel, Field


class ParcelIn(BaseModel):
    recipient: str
    zip_code: str = Field(pattern=r"^[0-9]{4}$")
    weight_kg: float = Field(gt=0, le=30)


class Parcel(ParcelIn):
    id: int
    status: str = "registered"
    price_chf: float
