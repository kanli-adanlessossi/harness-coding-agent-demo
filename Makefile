PY ?= python3
WS ?= $(HOME)/post-agent-demo-ws

.PHONY: install test sanity workspace evals compare clean

install:          ## install Python dependencies
	$(PY) -m pip install -r requirements.txt

test:             ## unit tests: hook, MCP server, eval harness, sample service
	$(PY) -m pytest -q

sanity:           ## prove every eval task is solvable and every check meaningful
	$(PY) evals/run_evals.py --agent reference --expect all-pass
	$(PY) evals/run_evals.py --agent none --expect all-fail

workspace:        ## fresh demo workspace for a live session (WS=path)
	$(PY) scripts/new_workspace.py $(WS)

evals:            ## real agent run (needs ANTHROPIC_API_KEY)
	$(PY) evals/run_evals.py --agent claude --repeat 3 --out results/head.json

compare:          ## compare results/base.json with results/head.json
	$(PY) evals/compare.py results/base.json results/head.json

clean:
	rm -rf results .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
