# Security

## Secrets

- Anthropic credentials must stay in the Modal secret named `anthropic-secret` unless `agent_sandbox/config/settings.py` is explicitly changed.
- Never commit API keys, run logs containing secrets, or user-derived data.
- The Claude-driven path requires `ANTHROPIC_API_KEY`; the direct baseline path does not.

## Runtime Boundaries

- The wrapper repo contains orchestration and documentation, not the upstream research code or experiment history.
- Experiment git operations that matter happen inside the cloned upstream checkout on the Modal workspace volume.
- Claude CLI runs as the non-root `claude` user inside the Modal image.

## Review Checklist

- Secret names and required keys match the typed settings surface.
- New environment variables are documented in `agent_sandbox/config/settings.py` and reflected in generated docs if applicable.
- No new docs or tests expose credential material.
