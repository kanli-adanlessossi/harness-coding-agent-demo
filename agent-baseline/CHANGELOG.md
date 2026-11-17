# Baseline changelog

Every change to the agent baseline gets a version, a changelog entry and an eval
comparison against the previous version (see `.github/workflows/agent-evals.yml`).
Roll back by reverting the commit or installing the previous tag.

## 1.0.0

- Ground rules in `CLAUDE.md` (look up rules, tests, small diffs, no secrets, no destructive actions)
- Skills: `rest-endpoint`, `fix-bug`
- Permissions: allow tests and read-only git, ask for push and installs, deny network and `.env` reads
- Guard hook: blocks secrets, `.env` writes and destructive shell commands, with audit log
- MCP: `post-docs` (read-only internal documentation)
