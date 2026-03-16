# Product Spec: autoresearch-modal

## Problem

Operators need a small, dependable wrapper repo that can prepare and validate `karpathy/autoresearch` runs on Modal without mixing that orchestration code into the upstream research repo.

## Users

- Engineers running baseline experiments on Modal
- Coding agents that need a repo-local map of the supported workflow

## In Scope

- Prepare a persistent upstream checkout per run tag
- Warm and reuse the upstream cache volume
- Run one direct GPU baseline
- Run one bounded Claude-driven baseline
- Capture the workflow, constraints, and validation evidence in repo-local docs

## Out Of Scope

- Owning or modifying the upstream research roadmap
- Becoming a general-purpose agent sandbox
- Shipping a user-facing web interface

## Supported Flows

1. Probe the Modal environment for required tools.
2. Prepare a run workspace and cache for a fresh `run_tag`.
3. Run one direct baseline and append a `results.tsv` row.
4. Optionally run one bounded Claude session against the same prepared checkout.

## Success Signals

- A new run tag produces a ready upstream checkout and cache state on Modal.
- The direct baseline completes and emits a parsable summary block.
- The Claude-driven baseline stays bounded and writes one upstream-compatible results row.
- Agents can find current product intent from the repo without external context.

## Constraints

- Local Modal CLI usage should stay on Python 3.11.
- Upstream branch creation starts from `master`.
- The cache volume must stay mounted at `/home/claude/.cache/autoresearch`.
- Anthropic credentials stay in the Modal secret configured by `Settings`.
