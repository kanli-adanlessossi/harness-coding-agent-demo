# API Conventions (demo)

> Fictional example document for the coding-agent demo.

## Endpoints

- Resource paths are plural nouns: `/parcels`, `/parcels/{parcel_id}`.
- Sub-resources hang off the parent: `/parcels/{parcel_id}/status`.
- Path and JSON field names use `snake_case`.

## Errors

- Unknown resources return `404` with body `{"detail": "<Resource> not found"}`.
- Invalid input returns `422`. Prefer declarative Pydantic validation
  (`Field(gt=0, le=30)`, `pattern=...`) over manual checks.

## Validation rules for parcels

- `weight_kg` must be greater than 0 and at most 30.
- `zip_code` is a Swiss postal code: exactly four digits (`^[0-9]{4}$`).

## Money

- Amounts are in CHF, rounded to two decimals (`round(x, 2)`).

## Tests

- Every new endpoint or rule needs a pytest test in `tests/`.
- Run the full suite with `python -m pytest -q` before finishing.
