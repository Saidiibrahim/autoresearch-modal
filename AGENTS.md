# Repository Guidelines

## Project Structure & Module Organization

This workspace is `autoresearch-modal`, an `autoresearch`-focused Modal wrapper. Keep it narrow: the repo exists to prepare a persistent upstream checkout, run baseline experiments on Modal, and support bounded Claude-driven runs against `karpathy/autoresearch`.

- `agent_sandbox/autoresearch_app.py`: the dedicated Modal app and all public Modal entrypoints.
- `agent_sandbox/autoresearch/`: pure helpers for run tags, path layout, log parsing, and prompt construction.
- `agent_sandbox/config/settings.py`: small Pydantic settings surface for the autoresearch runtime.
- `agent_sandbox/utils/cli.py`: Claude CLI user/env helpers reused by the Modal runtime.
- `docs/autoresearch-modal.md`: operational runbook with exact commands and caveats.
- `.agent/plans/autoresearch_modal/` and `.agent/tasks/autoresearch_modal/`: the active plan and task pack for this migration.

Do not reintroduce the old generic sandbox/controller/Ralph surface unless the user explicitly asks for it.

## Build, Test, and Development Commands

This is a **uv-based project**. Always activate the virtual environment before running commands.

### Setup

- `source .venv/bin/activate` — activate the virtual environment.
- `uv sync --group dev --python 3.11` — sync local dependencies and keep Modal CLI calls on Python 3.11.

### Running

- `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::probe_autoresearch_environment` — verify the Modal image has `python`, `git`, and `claude`.
- `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::prepare_autoresearch_run --run-tag <tag> --num-shards 10` — prepare persistent workspace and cache state.
- `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_baseline --run-tag <tag>` — run one direct GPU baseline.
- `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_with_claude --run-tag <tag>` — run the bounded Claude-driven baseline flow.

### Testing

- `uv run pytest` — run the full local test suite.
- `uv run pytest tests/test_autoresearch_core.py -q` — run focused helper coverage.

## Coding Style & Naming Conventions

Target Python 3.11+ features only when they remain compatible with Modal runtime images. Follow PEP 8 defaults: 4-space indentation, snake_case for functions and variables, UpperCamelCase for classes. Keep module-level constants uppercase. Prefer type hints on new functions, and keep environment and helper names explicit.

## Pre-commit Hooks

The repository uses Ruff for linting and formatting.

### Required: Run After Making Changes

Always run the Ruff linter and formatter after making code changes:

```bash
uv run ruff check --fix .
uv run ruff format .
```

## Testing Guidelines

Keep tests focused on deterministic helpers unless the user explicitly asks for heavier integration coverage. Before submitting changes, rerun Ruff, the local pytest suite, and the relevant Modal commands for the autoresearch flow you touched. Mark genuinely long-running checks with `@pytest.mark.slow`. Capture exact command output details in the final handoff.

## Commit & Pull Request Guidelines

Existing commits in ancestor repos used short, present-tense statements. Continue that style if the repo is reinitialized for git later. For PRs, include a concise summary, exact reproduction commands, and validation results.

## Security & Secrets

Never hardcode API keys. Anthropic credentials must stay in the Modal secret named `anthropic-secret` with key `ANTHROPIC_API_KEY` unless the user explicitly changes the configured secret name in `agent_sandbox/config/settings.py`. Avoid committing generated artifacts that might expose credentials or user data.

## ExecPlans

When writing complex features or refactoring, create or update an ExecPlan as described in `.agent/plans/Plan.md`. For this workspace, continue updating `.agent/plans/autoresearch_modal/PLAN_autoresearch_modal.md` and its task files instead of creating disconnected plan packs unless the user explicitly changes scope. Place any temporary research or clones in a `.gitignored` subdirectory of `.agent/`.
