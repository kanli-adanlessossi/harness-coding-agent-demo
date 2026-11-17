# Coding Agent Baseline: a small, testable example

A small, complete example of how a team can **ship a coding agent as a product**:
preconfigured with rules and skills, connected to internal knowledge over MCP,
guarded by hooks, and measured by evals on every change.

```
agent-baseline/            the "product": what every developer gets
  CLAUDE.md                ground rules
  .claude/settings.json    permissions (allow / ask / deny) + hook wiring
  .claude/skills/          rest-endpoint, fix-bug
  .claude/hooks/guard.py   blocks secrets, .env writes, destructive commands; audit log
  VERSION, CHANGELOG.md    versioned, easy to roll back
mcp_server/                post-docs: read-only MCP server for internal docs
sample_service/            small FastAPI parcel service the agent works on
evals/
  tasks/<id>/              prompt, hidden check test, reference solution
  run_evals.py             runs the agent in fresh workspaces, scores results
  compare.py               "better, or just different?" between two runs
tests/                     tests for the hook, the MCP server and the eval harness
.github/workflows/         CI (deterministic) + agent evals on baseline changes
```

## Quick start

```bash
pip install -r requirements.txt
make test      # 37 tests: hook, MCP server, eval harness, sample service
make sanity    # every task solvable by the reference, every check fails on untouched code
```

With [Claude Code](https://docs.claude.com/en/docs/claude-code) and an API key:

```bash
make workspace WS=~/demo-ws     # sample service + baseline + MCP config
cd ~/demo-ws && claude          # work with the configured agent
make evals                      # real agent, 3 attempts per task
```

## The pieces

### 1. Baseline configuration and skills

`CLAUDE.md` holds a few ground rules that matter, not a wall of text. Skills
encode repeatable workflows (`rest-endpoint`, `fix-bug`) and point the agent to the
internal docs instead of letting it guess business rules.

### 2. MCP: internal knowledge, read-only

`mcp_server/server.py` exposes `list_docs`, `search_docs` and `get_doc`, all
annotated as read-only. In the eval workspaces the docs exist **only** behind MCP,
so the `saturday-surcharge` task can be solved only if the agent actually uses it.
The same pattern works for Confluence, Backstage, Jira or internal APIs.

### 3. Safety where the agent acts

Two layers, so the safe path is also the easy one:

- **Permissions** (`settings.json`): tests and read-only git allowed; push and
  installs need confirmation; network tools and `.env` reads denied.
- **Guard hook** (`guard.py`, `PreToolUse`): blocks secrets in written files or
  commands, `.env` writes, `rm -rf`, force pushes, `curl | sh`, `--no-verify`.
  It explains *why* to the agent, so the agent picks a safer route, and writes
  an audit entry without the secret. It fails closed and has its own test suite.

### 4. Evals: better, or just different?

Each task has a prompt, a **hidden** check test (copied in after the agent
finishes) and a reference solution. A task passes only if the hidden check and all
existing tests are green, so regressions count as failures.

| Task | What it measures |
|---|---|
| add-status-endpoint | following API conventions for a new endpoint |
| validate-input | looking up validation rules instead of inventing them |
| fix-tariff-boundary | test-first bug fixing at an "inclusive" boundary |
| saturday-surcharge | using MCP for knowledge that is not in the repo |
| no-hardcoded-secret | keeping a pasted secret out of the repo (rules + hook) |

The harness checks itself: the `reference` agent must pass everything and the
`none` agent must fail everything. Otherwise a task is unsolvable or a check
tests nothing.

`compare.py` gives a verdict per task (*better*, *worse*, *same quality, cheaper*,
*no measurable change*) and fails CI on regressions. Agents are
non-deterministic, so use `--repeat 3` or more before trusting small differences.

**Evaluating a new model** on the same real tasks:

```bash
python evals/run_evals.py --agent claude --model <model-id> --repeat 3 --out results/new-model.json
python evals/compare.py results/head.json results/new-model.json
```

### 5. Release and rollback

Every baseline change goes through a PR. `agent-evals.yml` runs the agent with
the old and the new baseline and posts the comparison. Release by tagging
(`baseline-v1.1.0`), roll back with `git revert`.

## Try a change

Remove rule 1 ("Look things up, don't guess") from `agent-baseline/CLAUDE.md`
and the MCP hints from the skills, then run the evals again and compare. The
tasks that depend on internal rules should get worse, and the comparison will
show it.

## Notes

- Prices and rules in `mcp_server/docs` are invented for the demo.
- The guard hook uses pattern matching and is one layer, not a full secret
  scanner. In production, add a dedicated scanner (for example gitleaks) in CI
  and run the agent in a sandboxed container.
