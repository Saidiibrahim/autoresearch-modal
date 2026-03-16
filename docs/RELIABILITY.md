# Reliability

## Validation Matrix

Run these in the repo virtualenv after changes:

```bash
source .venv/bin/activate
uv run ruff check --fix .
uv run ruff format .
uv run pytest
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::probe_autoresearch_environment
```

Run these when the Modal runtime, settings, prompt, or orchestration path changes:

```bash
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::prepare_autoresearch_run --run-tag <tag> --num-shards 10
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_baseline --run-tag <tag>
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_with_claude --run-tag <tag>
```

## Expectations

- Keep Python 3.11 for local Modal CLI calls.
- Treat the direct baseline as the fastest end-to-end smoke.
- Treat the Claude-driven baseline as the full agent workflow proof when secrets are present.
- Record new evidence in the relevant completed plan or runbook update.

## Failure Handling

- Separate local environment failures from repo regressions.
- Preserve exact failing commands and the smallest useful tail of output.
- If remote validation is skipped, say so explicitly and do not imply current proof.
