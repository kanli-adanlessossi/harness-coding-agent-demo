# Tariff Guideline (demo)

> Fictional prices for the coding-agent demo. Not real Swiss Post tariffs.

## Weight tiers

The upper bound of each tier is inclusive.

| Weight             | Price (CHF) |
|--------------------|-------------|
| up to and including 2 kg  | 7.00  |
| up to and including 10 kg | 9.70  |
| up to and including 30 kg | 20.50 |

Parcels heavier than 30 kg are not accepted.

## Saturday delivery surcharge

Customers can request Saturday delivery with the boolean field
`saturday_delivery` (default `false`). If requested, a flat surcharge of
**CHF 4.80** is added to the weight-tier price.

## Rounding

The final price is rounded to two decimals.
