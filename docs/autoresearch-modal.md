# autoresearch-modal

`autoresearch-modal` is a dedicated Modal wrapper for running [karpathy/autoresearch](https://github.com/karpathy/autoresearch.git) without vendoring the upstream project into this repository.

The operational entry module is:

- `agent_sandbox.autoresearch_app`

It clones the upstream repo into a persistent Modal workspace volume, keeps `~/.cache/autoresearch` on a separate persistent cache volume, and supports both:

- a deterministic direct baseline run
- a bounded Claude-driven baseline run that exercises the Claude CLI and git workflow on Modal

## Requirements

1. Activate the repo virtualenv and install dependencies:

```bash
source .venv/bin/activate
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

## Runtime layout

Default settings live in `agent_sandbox/config/settings.py`.

- Workspace volume: `autoresearch-workspace`
- Cache volume: `autoresearch-cache`
- Workspace mount: `/home/claude/workspaces/autoresearch`
- Cache mount: `/home/claude/.cache/autoresearch`
- Upstream base branch: `master`
- Experiment branch format: `autoresearch/<run_tag>`

Each run tag gets its own persistent checkout at:

```text
/home/claude/workspaces/autoresearch/<run_tag>/repo
```

## Commands

### 1. Probe the image and CLI surface

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::probe_autoresearch_environment
```

This validates that the Modal image has `python`, `git`, and `claude` available.

### 2. Prepare a run workspace and cache

Pick a fresh tag, for example `mar16smoke`. The upstream repo expects a new branch `autoresearch/<run_tag>` from `master`.

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::prepare_autoresearch_run --run-tag mar16smoke --num-shards 10
```

This:

- clones or refreshes `karpathy/autoresearch`
- checks out `autoresearch/mar16smoke`
- creates `results.tsv` if needed
- runs `python prepare.py --num-shards 10` when `~/.cache/autoresearch` is not ready
- keeps Triton and TorchInductor caches under the mounted cache volume instead of `/home/claude/.triton`

### 3. Run one direct baseline experiment

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_baseline --run-tag mar16smoke
```

This uses a GPU-backed Modal function, runs upstream `train.py` once, parses the summary block, and appends a `baseline` row to `results.tsv`.

### 4. Run the bounded Claude baseline flow

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_with_claude --run-tag mar16claude
```

This path:

- reuses the prepared workspace/cache
- invokes Claude CLI inside the GPU container as the non-root `claude` user
- uses git CLI directly inside the cloned repo
- performs exactly one baseline run and stops

## Convenience local entrypoint

You can also use the app’s local entrypoint:

```bash
source .venv/bin/activate
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode probe
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode prepare --run-tag mar16smoke
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode baseline --run-tag mar16smoke
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode claude-baseline --run-tag mar16claude
```

## Notes and constraints

- Upstream `autoresearch` currently uses `master`, not `main`.
- The direct baseline path does not require `ANTHROPIC_API_KEY`; the Claude path does.
- Use a fresh `run_tag` when you want a brand-new experiment branch and results file.
- The default GPU is `H100`, configurable through `AUTORESEARCH_GPU`.
- `prepare.py` writes to `~/.cache/autoresearch`, so the cache volume must stay mounted at that exact path for compatibility with upstream code.
- `TRITON_CACHE_DIR` and `TORCHINDUCTOR_CACHE_DIR` are redirected into the mounted cache volume. That fixes the non-root permission issue that originally blocked baseline runs.
- In this workspace, Modal CLI calls were reliable under Python 3.11. A Python 3.14-created `.venv` triggered a local `grpclib` assertion before requests reached Modal.
- The root wrapper repo currently has no `.git` directory by design. Git operations that matter happen inside the cloned upstream repo on the workspace volume.
