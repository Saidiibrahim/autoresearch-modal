# autoresearch-modal

`autoresearch-modal` is a focused Modal wrapper around [karpathy/autoresearch](https://github.com/karpathy/autoresearch.git). It no longer tries to be a generic agent sandbox or Claude SDK starter. The supported workflow is:

1. prepare a persistent upstream checkout and cache on Modal
2. run a direct 5-minute baseline on a GPU
3. optionally run a bounded Claude-driven baseline in the same repo/cache layout

The operational entrypoint remains `agent_sandbox.autoresearch_app`.

## Repo Shape

```text
agent_sandbox/
├── autoresearch_app.py        # Modal app, image, and public entrypoints
├── autoresearch/             # Pure helpers for paths, parsing, and prompts
├── config/settings.py        # Autoresearch-only runtime settings
└── utils/cli.py              # Claude CLI user/env helpers

docs/autoresearch-modal.md    # Detailed runbook
tests/test_autoresearch_core.py
tests/test_settings.py
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

## Commands

Probe the image and CLI surface:

```bash
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::probe_autoresearch_environment
```

Prepare a persistent run workspace and upstream cache:

```bash
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::prepare_autoresearch_run --run-tag mar16smoke --num-shards 10
```

Run one direct baseline:

```bash
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_baseline --run-tag mar16smoke
```

Run the bounded Claude-driven baseline:

```bash
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app::run_autoresearch_with_claude --run-tag mar16claude
```

Or use the local entrypoint modes:

```bash
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode probe
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode prepare --run-tag mar16smoke --num-shards 10
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode baseline --run-tag mar16smoke
uv run --python 3.11 modal run -m agent_sandbox.autoresearch_app --mode claude-baseline --run-tag mar16claude
```

## Runtime Contract

- Upstream default branch is `master`.
- Experiment branches are created as `autoresearch/<run_tag>`.
- `prepare.py` writes to `~/.cache/autoresearch`, so the cache volume must remain mounted at `/home/claude/.cache/autoresearch`.
- `train.py` is the file the research loop changes upstream.
- Triton and TorchInductor caches are redirected into the mounted cache volume via `TRITON_CACHE_DIR` and `TORCHINDUCTOR_CACHE_DIR`. Do not remove that routing.
- Local Modal CLI calls should use Python 3.11. The prior Python 3.14 local environment hit a `grpclib` assertion before requests reached Modal.

## Validated Results

The Modal path was already proved in this wrapper before the cleanup work:

- `prepare --run-tag mar16smoke --num-shards 10` produced branch `autoresearch/mar16smoke` and repo path `/home/claude/workspaces/autoresearch/mar16smoke/repo`.
- Direct baseline on `mar16smoke` finished with `val_bpb=0.996024`, `training_seconds=300.1`, `peak_vram_mb=45060.2`, `num_steps=940`.
- Claude-driven baseline on `mar16claude` finished on branch `autoresearch/mar16claude` at commit `c2450ad` with `val_bpb=0.995971`, `training_seconds=300.1`, `peak_vram_mb=45060.2`, `num_steps=939`.

See [docs/autoresearch-modal.md](docs/autoresearch-modal.md) for the full runbook and expected output shape.
