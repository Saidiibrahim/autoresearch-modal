# Architecture

## Purpose

`autoresearch-modal` exists to make one workflow legible and repeatable for coding agents:

1. prepare a persistent checkout of `karpathy/autoresearch` on Modal
2. warm and reuse the upstream cache
3. run one direct GPU baseline
4. optionally run one bounded Claude-driven baseline in the same checkout

This repo does not own the research code itself. It owns orchestration, guardrails, validation, and repository-local knowledge.

## Module Map

| Path | Responsibility |
| --- | --- |
| `agent_sandbox/autoresearch_app.py` | Modal app, image, volumes, public entrypoints, and subprocess orchestration |
| `agent_sandbox/autoresearch/core.py` | Pure helpers for path layout, run tags, results rows, prompt construction, and training-log parsing |
| `agent_sandbox/config/settings.py` | Typed runtime configuration and Modal secret wiring |
| `agent_sandbox/utils/cli.py` | Claude CLI environment and user helpers reused inside Modal |
| `tests/` | Deterministic coverage for settings and pure helpers |
| `docs/references/autoresearch-modal-runbook.md` | Exact operator commands and expected runtime behavior |

## Runtime Boundaries

- The wrapper repo is the knowledge and orchestration layer.
- The upstream `karpathy/autoresearch` checkout lives inside the Modal workspace volume.
- Persistent state is file-based:
  - workspace volume at `/home/claude/workspaces/autoresearch`
  - cache volume at `/home/claude/.cache/autoresearch`
  - upstream `results.tsv` inside each prepared checkout
- There is no first-party application database in this repo. The generated schema artifact currently snapshots the typed runtime settings surface instead.

## Execution Flow

1. Load `Settings` from environment and Modal secrets.
2. Build the Modal image with Python, git, Node, and Claude CLI available.
3. Mount persistent workspace and cache volumes.
4. Clone or refresh the upstream repo into `<workspace>/<run_tag>/repo`.
5. Ensure the branch `autoresearch/<run_tag>` exists from upstream `master`.
6. Warm the upstream cache with `prepare.py` when needed.
7. Run `train.py` directly or via a bounded Claude prompt.
8. Parse the upstream summary block and append a row to `results.tsv`.

## Knowledge System

- `AGENTS.md` is the table of contents.
- `docs/product-specs` holds current intent and workflow expectations.
- `docs/design-docs/` holds durable architecture and agent-operating beliefs.
- `docs/exec-plans/` holds active work, completed work, and tech debt.
- `docs/references/` holds operational runbooks and external reference pointers.
- `docs/generated/` holds code-derived artifacts that should be regenerated instead of hand-edited.

## Change Guidance

- If you change runtime behavior, update `ARCHITECTURE.md`, the product spec, and the runbook together.
- If you change durable process or governance, update `docs/design-docs/`, `docs/PLANS.md`, and `docs/exec-plans/index.md`.
- If you add persistence, replace the placeholder generated schema workflow with a real exporter and document the new source of truth in `docs/generated/db-schema.md`.
