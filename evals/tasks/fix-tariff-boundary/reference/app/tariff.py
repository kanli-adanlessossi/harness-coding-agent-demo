"""Parcel tariff.

Business rules live in the internal document "tariff-guideline"
(available to the coding agent through the post-docs MCP server).
"""

# (max weight in kg, inclusive; price in CHF)
TIERS = [(2.0, 7.00), (10.0, 9.70), (30.0, 20.50)]


def price_chf(weight_kg: float) -> float:
    for max_weight, price in TIERS:
        if weight_kg <= max_weight:
            return price
    raise ValueError("Parcel too heavy (max 30 kg)")
