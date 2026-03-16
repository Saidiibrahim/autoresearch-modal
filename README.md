# autoresearch-modal

`autoresearch-modal` is a focused Modal wrapper around [karpathy/autoresearch](https://github.com/karpathy/autoresearch.git). It keeps the repo narrow:

1. prepare a persistent upstream checkout and cache on Modal
2. run a direct GPU baseline
3. optionally run a bounded Claude-driven baseline in the same repo/cache layout

The operational entrypoint remains `agent_sandbox.autoresearch_app`.

## Start Here

- [AGENTS.md](AGENTS.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [Product specs](docs/product-specs)
- [Design docs](docs/design-docs/index.md)
- [Execution plans](docs/exec-plans/index.md)
- [Runbook](docs/references/autoresearch-modal-runbook.md)

## Repo Shape

```text
agent_sandbox/
├── autoresearch_app.py
├── autoresearch/
├── config/settings.py
└── utils/cli.py

docs/
├── product-specs
├── design-docs/
├── exec-plans/
├── generated/
└── references/

tests/
```

## Setup

```bash
source .venv/bin/activate
uv sync --group dev --python 3.11
uv run --python 3.11 modal setup
```

For the Claude-driven path, create the secret once:

```bash
uv run --python 3.11 modal secret create anthropic-secret ANTHROPIC_API_KEY=your_key_here
```

## Core Commands

```bash
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::probe_autoresearch_environment
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::prepare_autoresearch_run --run-tag mar16smoke --num-shards 10
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_baseline --run-tag mar16smoke
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_with_claude --run-tag mar16claude
```

## Validation

```bash
uv run ruff check --fix .
uv run ruff format .
uv run pytest
```

See [docs/references/autoresearch-modal-runbook.md](docs/references/autoresearch-modal-runbook.md) for the full operational flow and expected outputs.
