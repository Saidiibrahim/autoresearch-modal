# ExecPlan: autoresearch-agent-loop-modal

## Purpose / Big Picture

Shift `autoresearch-modal` from a baseline-proof wrapper to an agent-driven Modal runtime that follows the upstream `karpathy/autoresearch` workflow more closely. The repo should keep the direct baseline smoke, but the primary product contract should become: prepare a persistent upstream checkout, surface `program.md`, run an autonomous Claude-driven experiment loop, and inspect the run state/results/logs from repo-local entrypoints and docs.

## Context and Orientation

- Upstream `README.md` and `program.md` define the real research loop: the human edits `program.md`; the agent edits `train.py`, runs experiments, logs to `results.tsv`, keeps or discards changes, and continues autonomously.
- The current repo still treats Claude as an optional bounded baseline proof.
- The runtime entrypoint remains `agent_sandbox.autoresearch_app`, so the work should extend that surface instead of inventing a new module tree.

## Plan of Work

1. Add repo-local plan/task artifacts for the product-contract shift.
2. Extend the runtime with first-class `program.md` read/write surfaces and richer run inspection helpers.
3. Add a primary agent-loop prompt and Modal entrypoint that follows upstream `program.md` expectations more closely than the current one-shot baseline prompt.
4. Keep the direct baseline path as a deterministic smoke, but demote the one-shot Claude baseline to a secondary or legacy support path.
5. Rewrite the README, architecture, product spec, product-sense, reliability, security, generated settings snapshot, and runbook to reflect the new primary workflow.
6. Re-run focused validation, capture results in this plan, and move the plan pack to completed.

## Concrete Steps

Task files live in `tasks/`.

## Progress

- [x] TASK_01_autoresearch_agent_loop_modal.md (2026-03-16 15:48 ACDT) Added first-class `program.md` read/write surfaces, a primary `run_autoresearch_agent_loop` entrypoint, artifact tailing, run inspection, run-state persistence, and upstream-aligned `uv` execution.
- [x] TASK_02_autoresearch_agent_loop_modal.md (2026-03-16 16:02 ACDT) Rewrote the README, architecture, product spec, product-sense, reliability, security, runbook, AGENTS map, and generated settings snapshot around the upstream human/agent split.
- [x] TASK_03_autoresearch_agent_loop_modal.md (2026-03-16 16:12 ACDT) Re-ran local lint/tests, regenerated generated docs, and validated the new non-GPU Modal surfaces (`probe`, `get-program`, `inspect`, `set-program`).

## Decision Log

- Decision: Preserve `agent_sandbox.autoresearch_app` as the operational entrypoint while broadening the runtime contract around it.
- Rationale: The module path is already proven and documented; the missing piece is behavior and contract, not entrypoint identity.
- Date/Author: 2026-03-16 / Codex

## Testing Approach

- Run local pure-helper/unit coverage with `uv run pytest`.
- Run Ruff lint/format checks.
- Run the Modal probe locally.
- If feasible within this turn, run at least the non-destructive Modal path(s) that prove the new agent-loop and inspection surfaces are wired correctly; if remote validation is skipped, say so explicitly.

## Validation Results

- PASS: `uv run python scripts/generate_db_schema.py`
- PASS: `uv run ruff format .`
- PASS: `uv run ruff check --fix .`
- PASS: `uv run pytest`
- PASS: `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode probe`
- PASS: `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode get-program --run-tag mar16contract`
- PASS: `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode inspect --run-tag mar16contract --lines 10`
- PASS: `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode set-program --run-tag mar16contract --program-file /tmp/autoresearch_program_test.md` (returned `program_updated=false`, so the write path executed without changing behavior)
- SKIP: GPU-backed `run_autoresearch_baseline`, legacy `run_autoresearch_with_claude`, and the full `run_autoresearch_agent_loop` were not re-proven in this turn because they are materially more expensive and, for Claude-driven paths, depend on live secret-backed remote execution.

## Risks / Constraints / Follow-ups

- Modal CLI in this workspace must continue to use Python 3.11 locally.
- Long-running agent-loop proof is more expensive than the previous one-shot baseline, so this turn stopped at non-GPU remote checks after the runtime surface changed.
- The repo should keep its scope narrow: agent-driven autoresearch on Modal, not a general-purpose orchestration framework.
