# Coding Agent Baseline (demo)

You are working in a Python/FastAPI service. These rules apply to every task.

## Commands

- Run tests: `python -m pytest -q`
- The app lives in `app/`, tests in `tests/`.

## Ground rules

1. **Look things up, don't guess.** Business rules (tariffs, validation limits) and
   conventions are in the internal docs. Use the `post-docs` MCP tools
   (`search_docs`, `get_doc`) before implementing anything rule-based.
2. **Tests first or alongside.** Every change comes with a pytest test. Finish only
   when `python -m pytest -q` passes.
3. **Small, focused diffs.** Change only what the task needs.
4. **Secrets never go into files.** Read them from environment variables via
   `app/config.py`. If a user pastes a key, refer to the variable name instead and
   tell them where to set it. A guard hook will block secrets anyway.
5. **No destructive actions.** No recursive deletes, force pushes or piping
   downloads into a shell. Ask the human instead.

## Skills

- `rest-endpoint`: adding or changing an HTTP endpoint.
- `fix-bug`: reproducing and fixing a reported bug.
