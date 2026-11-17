# Security Guideline for Services and Agents (demo)

> Fictional example document for the coding-agent demo.

## Secrets

- Never write API keys, tokens or passwords into source code, tests, docs or `.env` files in the repository.
- Services read secrets from environment variables through `app/config.py`
  (for example `os.environ["TARIFF_API_KEY"]`).
- Locally, developers set secrets in their shell or a secret manager; in CI and
  production they come from the platform's secret store.
- If someone hands you a secret in a chat or ticket, do not copy it into the repo:
  reference the environment variable name instead and tell the person where to set it.

## Destructive actions

- No recursive force deletes, force pushes or `curl | sh` installs by the agent.
  Ask a human instead.

## Dependencies

- Add dependencies only with a pinned version and a short reason in the PR description.
