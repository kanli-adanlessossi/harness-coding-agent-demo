"""Parcel tariff.

Business rules live in the internal document "tariff-guideline"
(available to the coding agent through the post-docs MCP server).
"""

# (max weight in kg, price in CHF)
TIERS = [(2.0, 7.00), (10.0, 9.70), (30.0, 20.50)]
SATURDAY_SURCHARGE_CHF = 4.80


def price_chf(weight_kg: float, saturday_delivery: bool = False) -> float:
    for max_weight, price in TIERS:
        if weight_kg < max_weight:
            surcharge = SATURDAY_SURCHARGE_CHF if saturday_delivery else 0.0
            return round(price + surcharge, 2)
    raise ValueError("Parcel too heavy (max 30 kg)")
