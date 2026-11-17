---
name: fix-bug
description: Reproduce and fix a reported bug with a failing test first. Use when a user, ticket or customer reports wrong behaviour.
---

# Fix a reported bug

1. **Understand the expected behaviour.** If the bug concerns a business rule,
   look the rule up with `search_docs` (post-docs MCP). Pay attention to boundaries
   such as "up to and including".
2. **Reproduce.** Write a pytest test that fails for exactly the reported case,
   plus the neighbouring boundary cases. Run it and confirm it fails.
3. **Fix minimally.** Change the smallest amount of code that makes the test pass.
4. **Regression check.** Run the full suite with `python -m pytest -q`.
5. **Report.** Explain the root cause in one sentence and name the test that now
   guards against it.
