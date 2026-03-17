# Security

## Secrets

- Anthropic credentials must stay in the Modal secret named `anthropic-secret` unless `agent_sandbox/config/settings.py` is explicitly changed.
- Never commit API keys, run logs containing secrets, or user-derived data.
- The Claude-driven paths require `ANTHROPIC_API_KEY`; the direct baseline path does not.

## Runtime Boundaries

- The repo contains both the vendored upstream research files and the Modal orchestration/documentation layers.
- Experiment git operations that matter happen inside the per-run workspace repo on the Modal workspace volume.
- Claude CLI runs as the non-root `agent` user inside the Modal image.
- The human steers `program.md`; the agent loop should only edit `train.py` plus uncommitted runtime artifacts like `results.tsv` and `run.log`.

## Review Checklist

- Secret names and required keys match the typed settings surface.
- New environment variables are documented in `agent_sandbox/config/settings.py` and reflected in generated docs if applicable.
- No new docs or tests expose credential material.
- Inspection surfaces do not leak secrets by dumping more log output than necessary.
