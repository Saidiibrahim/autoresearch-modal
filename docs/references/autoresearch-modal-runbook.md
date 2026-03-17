# Autoresearch Modal Runbook

`autoresearch-modal` is a dedicated Modal runtime for running a vendored copy of [karpathy/autoresearch](https://github.com/karpathy/autoresearch.git) that lives directly in this repository.

Read this after `AGENTS.md`, `ARCHITECTURE.md`, and the product spec when you need exact operator commands.

The repo root already carries the upstream top-level file set in merged form:

- `.gitignore`
- `.python-version`
- `README.md`
- `analysis.ipynb`
- `prepare.py`
- `program.md`
- `progress.png`
- `pyproject.toml`
- `train.py`
- `uv.lock`

## Requirements

1. Create or update the repo virtualenv and install dependencies:

```bash
uv sync --group dev --python 3.11
```

2. Ensure Modal is configured:

```bash
uv run --python 3.11 modal setup
```

3. For the Claude-driven path, publish the Anthropic key to Modal:

```bash
uv run --python 3.11 modal secret create anthropic-secret ANTHROPIC_API_KEY=your_key_here
```

## Runtime Layout

Default settings live in `agent_sandbox/config/settings.py`.

- Source project root in the Modal image: `/home/agent/app`
- Workspace volume: `autoresearch-workspace`
- Cache volume: `autoresearch-cache`
- Workspace mount: `/home/agent/workspaces/autoresearch`
- Cache mount: `/home/agent/.cache/autoresearch`
- Upstream base branch: `master`
- Experiment branch format: `autoresearch/<run_tag>`

Each run tag gets its own persistent workspace repo at:

```text
/home/agent/workspaces/autoresearch/<run_tag>/repo
```

Workspace seeding uses an explicit upstream-root allowlist. A fresh run repo root should contain exactly:

- `.gitignore`
- `.python-version`
- `README.md`
- `analysis.ipynb`
- `prepare.py`
- `program.md`
- `progress.png`
- `pyproject.toml`
- `train.py`
- `uv.lock`

Wrapper-owned top-level surfaces (`AGENTS.md`, `ARCHITECTURE.md`, `agent_sandbox/`, `docs/`, `scripts/`, `tests/`) stay in the source repo and are not copied into run repos.

The run root also carries wrapper-owned inspection artifacts:

```text
/home/agent/workspaces/autoresearch/<run_tag>/prepare.log
/home/agent/workspaces/autoresearch/<run_tag>/agent.log
/home/agent/workspaces/autoresearch/<run_tag>/modal-run-state.json
```

## Commands

### 1. Probe the image and CLI surface

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::probe_autoresearch_environment
```

This validates that the Modal image has `python`, `git`, and `claude` available.

### 2. Prepare a run workspace and cache

For a first-time run you may omit `--run-tag`, and the runtime will generate one for you. The upstream repo still expects the branch `autoresearch/<run_tag>` from `master`, so save the returned tag for later commands.

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::prepare_autoresearch_run --num-shards 10
```

This:

- seeds the workspace repo from the upstream-root allowlist on first use
- checks out `autoresearch/<returned-run-tag>`
- exposes upstream `program.md` in the prepared checkout
- creates `results.tsv` if needed
- runs `uv run prepare.py --num-shards 10` when `~/.cache/autoresearch` is not ready
- keeps Triton, TorchInductor, and uv caches under the mounted cache volume
- returns the actual `run_tag` in the payload; later `inspect`, `tail`, `get-program`, `set-program`, or resume flows must use that exact tag

### 3. Read or update `program.md`

Inspect the current program:

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode get-program --run-tag <returned-run-tag>
```

Update it from a local file:

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode set-program --run-tag <returned-run-tag> --program-file ./program.md
```

This keeps the upstream `program.md` as the human-controlled control plane for that run tag.

### 4. Run one direct baseline smoke

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_baseline
```

This uses a GPU-backed Modal function, runs upstream `train.py` once, parses the summary block, appends a `baseline` row to `results.tsv`, and returns the actual `run_tag` used for the run.

### 5. Run the primary agent loop

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode agent-loop --max-experiments 12 --max-turns 200
```

This path:

- reuses the prepared workspace/cache
- expects the human to have already shaped `program.md`
- invokes Claude CLI inside the GPU container as the non-root `agent` user
- uses git CLI directly inside the workspace repo
- follows the upstream research loop more closely: the agent edits `train.py`, runs experiments, logs to `results.tsv`, and keeps or discards changes without human confirmation
- returns the chosen `run_tag`; keep it if you want to inspect or resume that run later

### 6. Inspect or tail the current run

Inspect the current state:

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode inspect --run-tag <returned-run-tag> --lines 30
```

The inspect payload reports `workspace_seed_source: "vendored-project-root-allowlist"` and `repo_root_files`; use those fields to confirm no wrapper-owned top-level entries leaked into a fresh run repo.

Tail a specific artifact:

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode tail --run-tag <returned-run-tag> --artifact agent --lines 80
```

Supported `artifact` values are `agent`, `prepare`, `results`, `run`, `program`, and `state`.

### Legacy one-shot Claude baseline

The previous bounded Claude baseline still exists if you need one focused smoke/debug run:

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_with_claude --run-tag mar16claude
```

## Convenience Local Entrypoint

You can also use the app’s local entrypoint:

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode probe
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode prepare
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode get-program --run-tag <returned-run-tag>
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode set-program --run-tag <returned-run-tag> --program-file ./program.md
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode baseline
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode agent-loop --max-experiments 12 --max-turns 200
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode inspect --run-tag <returned-run-tag> --lines 30
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode tail --run-tag <returned-run-tag> --artifact agent --lines 80
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode claude-baseline --run-tag <returned-run-tag>
```

## Notes And Constraints

- Upstream `autoresearch` currently uses `master`, not `main`.
- The direct baseline path does not require `ANTHROPIC_API_KEY`; the Claude-driven paths do.
- `prepare`, `baseline`, and `agent-loop` can generate a fresh `run_tag` automatically, but `inspect`, `tail`, `get-program`, `set-program`, and `claude-baseline` still require an explicit one.
- The default GPU is `H100`, configurable through `AUTORESEARCH_GPU`.
- `prepare.py` writes to `~/.cache/autoresearch`, so the cache volume must stay mounted at that exact path for compatibility with upstream code.
- `TRITON_CACHE_DIR` and `TORCHINDUCTOR_CACHE_DIR` are redirected into the mounted cache volume. That fixes the non-root permission issue that originally blocked baseline runs.
- `UV_CACHE_DIR` is also routed into the mounted cache volume so upstream `uv` commands stay warm across sessions.
- In this workspace, Modal CLI calls were reliable under Python 3.11. A Python 3.14-created `.venv` triggered a local `grpclib` assertion before requests reached Modal.
- The repo is versioned locally, but the experiment git state that matters lives inside the per-run workspace repo on the workspace volume.
- The wrapper intentionally keeps the human/agent split from upstream: the human edits `program.md`; the agent loop edits `train.py`.
