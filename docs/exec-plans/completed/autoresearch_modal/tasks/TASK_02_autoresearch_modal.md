---
task_id: 02
plan_id: PLAN_autoresearch_modal
plan_file: ../PLAN_autoresearch_modal.md
title: Implement dedicated autoresearch Modal runtime
phase: Phase 2 - Runtime and Bootstrap
---

## Goal

Add the code needed to prepare, clone, branch, and run `autoresearch` on Modal using persistent workspace/cache volumes plus Claude CLI and git integration.

## Notes

- Prefer a dedicated module/app over deep edits to the legacy general-purpose service.
- Reuse shared CLI privilege-demotion helpers where possible.
- Keep both deterministic and Claude-driven execution paths available for validation and operational use.

## Exit Criteria

- Modal image and functions implemented.
- Repo/bootstrap helpers implemented and unit-testable.
- Claude CLI and git paths operate against the autoresearch workspace contract.
