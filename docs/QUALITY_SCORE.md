# Quality Score

- Owner: Repository maintainers
- Last reviewed: 2026-03-16
- Review cadence: weekly or after any material runtime or governance change

## Rubric

- `5` Strong: current, cross-linked, validated, and low-risk
- `4` Good: fit for purpose with minor follow-up debt
- `3` Fair: usable but missing evidence, freshness, or cross-links
- `2` Weak: notable drift or unclear ownership
- `1` Broken: cannot be trusted as current guidance

## Scorecard

| Area | Score | Notes |
| --- | --- | --- |
| Product intent | 4 | Spec and product-sense docs are now explicit and linked |
| Architecture legibility | 4 | Runtime map and docs taxonomy are present; a CI doc-lint is still missing |
| Plan hygiene | 4 | Active/completed split is in place and legacy plan history was migrated |
| Reference quality | 4 | Runbook moved under canonical references and linked from the top-level map |
| Generated artifacts | 3 | Schema doc is code-backed, but the repo still has no true DB exporter because there is no DB |
| Reliability evidence | 3 | Local checks are defined; full remote Modal proof should continue to be refreshed after runtime changes |
| Security posture | 4 | Secret handling is explicit and repo-local docs capture the boundary |

## Action Item Expectations

- Any area scored `3` or lower must have either:
  - an active execution plan, or
  - an entry in `docs/exec-plans/tech-debt-tracker.md`
- Re-score after meaningful code, docs, or operational workflow changes.
- Prefer score changes backed by concrete validation evidence, not opinion alone.
