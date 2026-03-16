# ExecPlan: autoresearch-modal

Historical note: this completed plan was migrated into the canonical `docs/exec-plans/` layout on 2026-03-16. The work below reflects the original repository cleanup and runtime proof, with path references repaired for the new docs taxonomy.

## Purpose / Big Picture

Finish repurposing this old wrapper repo into `autoresearch-modal`. The final repo should have one clear job: clone `karpathy/autoresearch` into persistent Modal volumes, prepare the shared cache, run direct GPU baselines, and run bounded Claude-driven baselines against upstream branches.

## Surprises & Discoveries

- Observation: Upstream `autoresearch` creates experiment branches from `master`, not `main`.
- Evidence: `/tmp/autoresearch.AKMp4P/program.md` says to create `autoresearch/<tag>` from current `master`, and `git symbolic-ref refs/remotes/origin/HEAD` in the clone resolves to `refs/remotes/origin/master`.

- Observation: The only reusable legacy helper we needed after the cleanup was the non-root Claude CLI utility module.
- Evidence: The final repo keeps `agent_sandbox/utils/cli.py` and removes the old controller, Ralph, job, and tool stacks.

- Observation: Modal CLI execution from a Python 3.14-created local `.venv` failed before requests reached Modal, but the same commands worked when invoked with `uv run --python 3.11`.
- Evidence: Prior local `MODAL_TRACEBACK=1 uv run modal run ...` failed with a local `grpclib/events.py` `AssertionError: ()`, while the current `uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode probe` succeeds.

- Observation: The first GPU baseline attempt failed because Triton tried to write to `/home/claude/.triton`, which the `claude` user could not write.
- Evidence: The failing Modal baseline run returned `torch._inductor.exc.InductorError: PermissionError: [Errno 13] Permission denied: '/home/claude/.triton'`.

- Observation: Routing `TRITON_CACHE_DIR` and `TORCHINDUCTOR_CACHE_DIR` into the mounted cache volume removed the startup blocker and remains required after the cleanup.
- Evidence: The post-cleanup direct and Claude-driven baselines both completed successfully with parsed summaries and appended `results.tsv` rows.

- Observation: Experiment git operations that affect run branches still happen inside the cloned upstream repo on the Modal workspace volume.
- Evidence: The runtime bootstrap creates and manages `autoresearch/<run_tag>` inside `/home/claude/workspaces/autoresearch/<run_tag>/repo`.

- Observation: Once the legacy test surface and incompatible dependencies were removed, full local pytest collection became clean again.
- Evidence: `uv run pytest -q` now reports `13 passed in 0.21s`.

## Decision Log

- Decision: Keep the upstream `autoresearch` repo external and clone/sync it into a persistent Modal workspace volume at runtime.
- Rationale: This preserves a clean boundary between the wrapper/orchestration repo and the research repo while keeping it easy to refresh upstream state.
- Date/Author: 2026-03-16 / Codex

- Decision: Keep the verified module entrypoint `agent_sandbox.autoresearch_app` even while deleting the rest of the old generic `agent_sandbox` surface.
- Rationale: The module path was already proven on Modal, so preserving it avoided a gratuitous rename while still letting the repo become autoresearch-only.
- Date/Author: 2026-03-16 / Codex

- Decision: Simplify the wrapper package to four code areas only: Modal runtime, pure autoresearch helpers, small settings, and Claude CLI helpers.
- Rationale: Everything else in the repo was legacy scaffolding unrelated to the user’s stated objective and was causing dependency/test drift.
- Date/Author: 2026-03-16 / Codex

- Decision: Keep both deterministic and Claude-driven execution paths.
- Rationale: A direct baseline is the most reliable end-to-end GPU smoke, while the Claude path specifically proves the requested Claude CLI + git workflow on Modal.
- Date/Author: 2026-03-16 / Codex

## Outcomes & Retrospective

The repo now has a clean autoresearch-only shape:

- kept: `agent_sandbox/autoresearch_app.py`, `agent_sandbox/autoresearch/`, `agent_sandbox/config/settings.py`, `agent_sandbox/utils/cli.py`, the autoresearch runbook, and focused tests
- removed: the old generic Modal app, controllers, jobs, prompts, schemas, services, tool registry, Ralph subsystem, example apps, legacy docs, legacy tests, and the stale `agent_sandbox_starter.egg-info` output
- simplified: `pyproject.toml`, `.gitignore`, `README.md`, and `AGENTS.md` now describe only the autoresearch Modal workflow

Runtime proof was re-captured after the cleanup on 2026-03-16:

- Probe: Python `3.11.12`, git `2.39.5`, Claude Code `2.1.76`
- Prepare on `autoresearch/mar16cleanupbase`: repo root `/home/claude/workspaces/autoresearch/mar16cleanupbase/repo`, cache already warm so `prepared=false`
- Direct baseline on `autoresearch/mar16cleanupbase`: `val_bpb=0.995657`, `training_seconds=300.3`, `peak_vram_mb=45060.2`, `num_steps=945`
- Claude-driven baseline on `autoresearch/mar16cleanupclaude`: `val_bpb=0.995915`, `training_seconds=300.2`, `peak_vram_mb=45060.2`, `num_steps=941`

The old full-suite blocker involving `claude-agent-sdk` and `mcp.ToolAnnotations` is no longer relevant because that legacy surface was intentionally retired from the repo.

## Context and Orientation

The wrapper remains intentionally small. Upstream `autoresearch` still defines the real research contract:

- `prepare.py` downloads data and trains the tokenizer into `~/.cache/autoresearch`
- `train.py` is the file the agent edits
- `program.md` defines the human/agent research loop
- each experiment should run on one GPU, train for about 5 minutes, and report `val_bpb`

The wrapper’s job is to supply a stable Modal image, persistent workspace/cache mounts, upstream branch/bootstrap logic, Claude CLI access, and parsed results.

## Plan of Work

1. Audit the remaining repo and upstream dependencies.
2. Isolate the true runtime keep-set and simplify configuration around it.
3. Remove the unrelated legacy code, docs, tests, and dependency graph.
4. Rewrite project identity and runbooks so the repo reads as autoresearch-first.
5. Re-run local and Modal validations on the cleaned tree.

## Concrete Steps

Task files live in `docs/exec-plans/completed/autoresearch_modal/tasks/`.

## Progress

[x] (TASK_01_autoresearch_modal.md) (2026-03-16 12:55) Audited the current repo, cloned upstream `autoresearch`, and verified the upstream branch/program contract plus relevant Modal docs/tools.

[x] (TASK_02_autoresearch_modal.md) (2026-03-16 14:18) Implemented the dedicated `autoresearch` package and Modal app with persistent workspace/cache volumes, direct baseline, and Claude-driven baseline flows.

[x] (TASK_03_autoresearch_modal.md) (2026-03-16 14:23) Added the initial autoresearch runbook, README coverage, and focused helper tests.

[x] (TASK_04_autoresearch_modal.md) (2026-03-16 15:12) Captured the first working Ruff/pytest/Modal proof for the dedicated autoresearch runner.

[x] (TASK_05_autoresearch_modal.md) (2026-03-16 13:37 ACDT) Removed the unrelated legacy project surface, simplified package identity/configuration, and revalidated the cleaned repo locally and on Modal.

## Testing Approach

Use unit tests for pure helpers such as branch naming, results file bootstrapping, prompt generation, settings defaults, and training-log parsing. Run `uv run ruff check --fix .` and `uv run ruff format .` after edits. Validate Modal integration with targeted remote commands: probe, prepare, direct baseline, and bounded Claude baseline.

## Constraints & Considerations

The Claude path depends on a valid Modal secret providing `ANTHROPIC_API_KEY`. The upstream training repo expects a single NVIDIA GPU and a persistent `~/.cache/autoresearch` directory. Modal CLI commands in this workspace should continue to use Python 3.11 locally. The wrapper repo is versioned locally, but the experiment git state that matters still lives inside the cloned upstream repo on the mounted workspace volume.
