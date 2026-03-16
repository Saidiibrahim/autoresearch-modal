# Planning Standard

## Purpose

Plans are versioned repo artifacts, not chat-only notes. Use them to make current intent, progress, decisions, and validation legible to future agents.

## When To Create A Plan

- Use a lightweight checklist for very small edits that fit in one reviewable diff.
- Use an execution plan for work that spans multiple files, multiple validation steps, or multiple sessions.
- Put every active execution plan under `docs/exec-plans/active/<slug>/`.

## Required Plan Shape

Each execution plan should include:

- purpose and user-visible outcome
- context and orientation for a cold reader
- plan of work
- progress log
- decision log
- validation approach
- risks, constraints, and follow-ups

## Task Files

Large plans should have task files beside the plan so progress can be updated incrementally. Recommended layout:

```text
docs/exec-plans/active/<slug>/
├── PLAN_<slug>.md
└── tasks/
    ├── TASK_01_<slug>.md
    └── TASK_02_<slug>.md
```

Recommended task frontmatter:

```yaml
---
task_id: 01
plan_id: PLAN_<slug>
plan_file: ../PLAN_<slug>.md
title: Describe the task
phase: Phase 1 - Describe the phase
status: active
---
```

## Lifecycle

1. Start the work in `docs/exec-plans/active/`.
2. Keep the progress and decision log current while implementing.
3. Move the plan pack to `docs/exec-plans/completed/` when validation is done.
4. Record leftover gaps in `docs/exec-plans/tech-debt-tracker.md`.

## Repository Hygiene

- Link plans to the canonical product, design, and reference docs they depend on.
- Keep completed plans immutable except for path-fix migrations, broken-link repair, or clearly-labeled historical corrections.
- Prefer durable checklists and exact commands over narrative-only status updates.
- Weekly doc-gardening should review plan freshness, stale links, and untracked follow-up debt.
