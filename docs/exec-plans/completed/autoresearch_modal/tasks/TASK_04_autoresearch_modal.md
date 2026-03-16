---
task_id: 04
plan_id: PLAN_autoresearch_modal
plan_file: ../PLAN_autoresearch_modal.md
title: Run formatting and Modal smoke validation
phase: Phase 4 - Final Proof
---

## Goal

Prove the new workflow is wired correctly with local checks and a real Modal smoke path.

## Notes

- Capture blockers separately from code defects.
- Prefer a deterministic smoke before a longer Claude-driven run.

## Exit Criteria

- Ruff and pytest run cleanly or with clearly classified pre-existing failures.
- At least one Modal smoke path completes or a concrete blocker is captured.
