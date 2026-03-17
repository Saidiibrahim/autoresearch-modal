---
task_id: 01
plan_id: PLAN_autoresearch_agent_loop_modal
plan_file: ../PLAN_autoresearch_agent_loop_modal.md
title: Extend runtime surfaces for upstream-style agent control
phase: Phase 1 - Runtime
status: completed
---

## Goal

Add the runtime entrypoints and helper changes needed to make agent-driven experimentation the primary path: `program.md` surfaces, an autonomous loop prompt, and inspection helpers.

## Acceptance

- `agent_sandbox.autoresearch_app` exposes a primary agent-loop entrypoint.
- Operators can read and update `program.md` for a run tag.
- Operators can inspect current repo/log/results state without opening the Modal volume manually.
