---
task_id: 05
plan_id: PLAN_autoresearch_modal
plan_file: ../PLAN_autoresearch_modal.md
title: Retire legacy repo surface and revalidate the cleaned project
phase: Phase 5 - Cleanup and Closure
---

## Goal

Remove the old generic agent-sandbox/Ralph project surface so the repo reads as `autoresearch-modal`, then re-run the validation matrix on the cleaned tree.

## Notes

- Delete legacy code, docs, tests, and dependency entries instead of preserving dead compatibility layers.
- Keep the proven `agent_sandbox.autoresearch_app` entrypoint unless there is a strong reason to rename it.
- Re-run both local and Modal proofs after the cleanup, because packaging and image installation changed.

## Exit Criteria

- The repo tree clearly centers on autoresearch-on-Modal only.
- Full local pytest is green without the old `claude-agent-sdk`/`mcp` blocker.
- Probe, prepare, direct baseline, and Claude-driven baseline all still work on Modal.
