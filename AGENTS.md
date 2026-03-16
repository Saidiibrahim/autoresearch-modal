# Agent Map

`autoresearch-modal` is a narrow Modal wrapper around `karpathy/autoresearch`. The repository itself is the system of record for agent context. Keep this file short and use it as a map.

## Read Order

1. `AGENTS.md`
2. `ARCHITECTURE.md`
3. `docs/product-specs`
4. `docs/design-docs/index.md`
5. `docs/PLANS.md`
6. `docs/exec-plans/index.md`
7. `docs/references/index.md`
8. `docs/generated/db-schema.md` when schema or state questions matter
9. Relevant code and tests

## Canonical Path Map

- Product intent: `docs/product-specs`
- Architecture and design: `ARCHITECTURE.md`, `docs/design-docs/`, `docs/DESIGN.md`
- Plans, tasks, and debt: `docs/exec-plans/`, `docs/PLANS.md`
- Operational references: `docs/references/`
- Reliability, quality, and security: `docs/RELIABILITY.md`, `docs/QUALITY_SCORE.md`, `docs/SECURITY.md`
- Generated schema artifacts: `docs/generated/`

## Routing By Work Type

- Runtime or Modal execution work: read `ARCHITECTURE.md`, `docs/references/autoresearch-modal-runbook.md`, and any relevant file under `docs/exec-plans/active/`
- Product or workflow changes: read the product specs directory and `docs/PRODUCT_SENSE.md`
- Design or repository-governance work: read `docs/design-docs/core-beliefs.md`, `docs/DESIGN.md`, and `docs/exec-plans/index.md`
- Reliability or validation work: read `docs/RELIABILITY.md`, `docs/QUALITY_SCORE.md`, and the relevant tests
- Security or secrets work: read `docs/SECURITY.md` and `agent_sandbox/config/settings.py`

## Working Rules

- Keep the scope narrow: persistent upstream checkout, cache prep, direct baseline runs, and bounded Claude-driven runs.
- Prefer durable repo-local docs over prompt-only guidance.
- New complex work starts under `docs/exec-plans/active/<slug>/` and moves to `docs/exec-plans/completed/` when finished.
- Keep `AGENTS.md` map-style. Put lasting detail in the docs tree, not here.
- Do not reintroduce generic sandbox or controller surfaces unless the user explicitly changes scope.

## Deprecated Layouts

- `docs/product-specs` is the only home for product specifications.
- `docs/exec-plans/` is the only home for execution plans and task tracking.
- Do not add new top-level spec trees or hidden plan/task trees.

## Validation

```bash
source .venv/bin/activate
uv run ruff check --fix .
uv run ruff format .
uv run pytest
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::probe_autoresearch_environment
```
