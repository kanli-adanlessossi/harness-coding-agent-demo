---
name: rest-endpoint
description: Add or change an HTTP endpoint in the FastAPI service following the internal API conventions. Use for any new route, new field or input validation.
---

# Add or change a REST endpoint

1. **Read the conventions.** Call `search_docs` (post-docs MCP) with the topic,
   e.g. "endpoints errors validation". If the task touches prices or rules, also
   search for them (e.g. "tariff surcharge"). Do not invent rules.
2. **Model first.** Add or change Pydantic models in `app/models.py`. Express
   validation declaratively (`Field(gt=0, le=30)`, `pattern=r"^[0-9]{4}$"`) so
   FastAPI returns `422` automatically.
3. **Route.** Add the route in `app/main.py`:
   - plural resource paths, sub-resources under the parent (`/parcels/{parcel_id}/status`)
   - `404` with `{"detail": "<Resource> not found"}` for unknown ids
   - keep business logic out of the route (e.g. prices belong in `app/tariff.py`)
4. **Test.** Add pytest tests in `tests/` covering the happy path and at least one
   error case, using `fastapi.testclient.TestClient`.
5. **Verify.** Run `python -m pytest -q`. Fix until green, then summarise the change
   in two or three sentences.
