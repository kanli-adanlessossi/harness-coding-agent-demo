"""In-memory parcel store (demo only)."""
from itertools import count

from .models import Parcel, ParcelIn


class ParcelStore:
    def __init__(self) -> None:
        self._parcels: dict[int, Parcel] = {}
        self._ids = count(1)

    def add(self, parcel: ParcelIn, price_chf: float) -> Parcel:
        stored = Parcel(id=next(self._ids), price_chf=price_chf, **parcel.model_dump())
        self._parcels[stored.id] = stored
        return stored

    def get(self, parcel_id: int) -> Parcel | None:
        return self._parcels.get(parcel_id)


store = ParcelStore()
