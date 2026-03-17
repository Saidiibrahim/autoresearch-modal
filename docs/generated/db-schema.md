# Generated Schema Snapshot

This repository does not currently own a first-party application database.
Until that changes, this generated artifact snapshots the typed runtime settings surface that agents most often need to inspect.

- Source: `agent_sandbox/config/settings.py` (`Settings`)
- Regenerate with: `uv run python scripts/generate_db_schema.py`

## Current Persistence Status

- Database tables: none
- Durable state lives in Modal volumes plus upstream `program.md`, `results.tsv`, and log files
- Wrapper-owned inspection state lives in per-run `modal-run-state.json` files

## Typed Runtime Settings

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `anthropic_api_key` | `str` | `""` |  |
| `anthropic_secret_name` | `str` | `anthropic-secret` | Modal secret that provides ANTHROPIC_API_KEY for Claude CLI runs. |
| `autoresearch_base_branch` | `str` | `master` | Git branch used when seeding a new autoresearch/<run_tag> branch in the workspace. |
| `autoresearch_workspace_vol_name` | `str` | `autoresearch-workspace` | Modal Volume name for persistent per-run workspace repos. |
| `autoresearch_cache_vol_name` | `str` | `autoresearch-cache` | Modal Volume name for ~/.cache/autoresearch and compiler caches. |
| `autoresearch_workspace_root` | `str` | `/home/agent/workspaces/autoresearch` | Mount path for the persistent per-run workspace volume. |
| `autoresearch_cache_root` | `str` | `/home/agent/.cache/autoresearch` | Mount path for the upstream cache volume. |
| `autoresearch_prepare_num_shards` | `int` | `10` | Shard count used by prepare.py when bootstrapping the cache. |
| `autoresearch_gpu` | `str` | `H100` | GPU type requested for direct baseline smokes and Claude-driven agent runs. |
| `autoresearch_prepare_timeout` | `int` | `3600` | Timeout in seconds for prepare_autoresearch_run. |
| `autoresearch_train_timeout` | `int` | `1200` | Timeout in seconds for one direct baseline run. |
| `autoresearch_claude_timeout` | `int` | `28800` | Timeout in seconds for one Claude-driven autoresearch session. |
| `autoresearch_git_user_name` | `str` | `Autoresearch Modal` | Git user.name configured inside the per-run workspace repo. |
| `autoresearch_git_user_email` | `str` | `autoresearch@modal.local` | Git user.email configured inside the per-run workspace repo. |

## Notes

- If this repo gains a database or durable structured store, replace this placeholder workflow with a real schema exporter.
- Keep this file generated; do not hand-edit it.
