---
task_id: 02
plan_id: PLAN_autoresearch_vendored_layout_modal
plan_file: ../PLAN_autoresearch_vendored_layout_modal.md
title: Replace runtime clone bootstrap with vendored project bootstrap
phase: Phase 2 - Runtime
status: completed
---

## Goal

Make the Modal runtime bootstrap from the vendored local project tree rather than cloning GitHub at run time.

## Acceptance

- Prepare/bootstrap no longer requires a remote clone.
- The per-run workspace still has a valid git baseline and the expected root files.
