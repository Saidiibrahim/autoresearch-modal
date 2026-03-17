# ExecPlan: autoresearch-vendored-layout-modal

## Purpose / Big Picture

Reshape `autoresearch-modal` so the repo contains the upstream `karpathy/autoresearch` files directly, instead of relying on a runtime clone from GitHub. The root should match the upstream layout as closely as practical while preserving the Modal runtime/docs surfaces that make the project operational.

## Context and Orientation

- The current runtime clones upstream `karpathy/autoresearch` into the Modal workspace volume on demand.
- The user wants the required upstream files to live in this repo directly and prefers using the full local directory in the Modal image.
- The likely steady-state is an “upstream-plus-Modal” root layout: `prepare.py`, `train.py`, `program.md`, `analysis.ipynb`, `progress.png`, and upstream dependency metadata at the root, with Modal-specific orchestration still in `agent_sandbox/` and repo docs in `docs/`.

## Plan of Work

1. Import the upstream repo files into the project root and merge packaging/ignore rules so the repo can run both locally and on Modal.
2. Replace the runtime clone/bootstrap logic with a workspace bootstrap that copies or initializes from the vendored local project tree instead of fetching from GitHub.
3. Update prompts, guardrails, tests, and docs so they describe the vendored layout and the new bootstrap contract precisely.
4. Run local validation and targeted Modal validation, then move the plan pack to completed.

## Concrete Steps

Task files live in `tasks/`.

## Progress

- [x] TASK_01_autoresearch_vendored_layout_modal.md (2026-03-16 17:34 ACDT) Vendored the upstream top-level file set into the repo root, merged the packaging/ignore rules, and added a layout test that asserts the expected root files exist.
- [x] TASK_02_autoresearch_vendored_layout_modal.md (2026-03-16 17:46 ACDT) Replaced runtime GitHub cloning with a vendored-project workspace seed, added repo-root inventory reporting, and tightened the image/workspace ignore list so CI/editor clutter is not copied into run workspaces.
- [x] TASK_03_autoresearch_vendored_layout_modal.md (2026-03-16 18:09 ACDT) Rewrote the repo docs around the vendored layout, regenerated the settings snapshot, and re-validated both the local toolchain and the non-GPU Modal seed path.

## Decision Log

- Decision: Keep the Modal runtime/documentation in this repo, but stop treating the upstream code as an external runtime dependency.
- Rationale: The user explicitly wants a repo that matches the upstream layout as closely as possible and carries the required files locally.
- Date/Author: 2026-03-16 / Codex
- Decision: Exclude local/CI-only files such as `.claude`, `.github`, and `.pre-commit-config.yaml` from the Modal image seed.
- Rationale: The run workspace should carry the vendored research/runtime tree, not editor or repository-maintenance baggage.
- Date/Author: 2026-03-16 / Codex

## Testing Approach

- Rebuild the generated settings snapshot if the settings surface changes.
- Run Ruff and pytest locally after the vendored files and runtime changes land.
- Re-run at least probe plus one non-GPU Modal path that exercises the new vendored bootstrap.

## Validation Results

- PASS: `uv lock`
- PASS: `uv sync --group dev --python 3.11`
- PASS: `uv run python scripts/generate_db_schema.py`
- PASS: `uv run ruff format .`
- PASS: `uv run ruff check --fix .`
- PASS: `uv run pytest`
- PASS: `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode inspect --run-tag mar16vendoredclean --lines 5`
  Returned `workspace_seed_source: "vendored-project-tree"` plus `repo_root_files` containing the expected vendored root files (`.gitignore`, `.python-version`, `README.md`, `analysis.ipynb`, `prepare.py`, `program.md`, `progress.png`, `pyproject.toml`, `train.py`, `uv.lock`) without the previously leaked `.claude`/`.github` entries.
- PASS: `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode probe`
  Returned `python: Python 3.11.12`, `git: git version 2.39.5`, `claude: 2.1.76 (Claude Code)`, `workspace_root: /home/claude/workspaces/autoresearch`, and `cache_root: /home/claude/.cache/autoresearch`.
- SKIP: GPU-backed `run_autoresearch_baseline`, `run_autoresearch_with_claude`, and `run_autoresearch_agent_loop` were not re-proven in this turn because the vendored-layout change was fully exercised by the non-GPU seed/inspect path and the GPU paths are materially more expensive.

## Risks / Constraints / Follow-ups

- The repo root already has wrapper-specific `README.md`, `pyproject.toml`, and `uv.lock`; these must be merged rather than blindly overwritten.
- The experiment workspace still needs git state, so vendoring files locally does not remove the need for per-run git bootstrap inside the Modal workspace.
- The vendored layout should not accidentally expose local-only editor/tooling files inside the runtime image.
