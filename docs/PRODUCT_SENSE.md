# Product Sense

## User Job

Give an agent or operator a clear, repeatable way to run bounded `autoresearch` experiments on Modal without vendoring the upstream repo into this wrapper.

## Priority Order

1. Reproducibility of the Modal workflow
2. Clarity of repo-local guidance
3. Narrow scope and low cognitive overhead
4. Fast validation loops with exact commands
5. Historical traceability through plans and references

## Non-Goals

- Becoming a general-purpose agent sandbox
- Owning the upstream `karpathy/autoresearch` codebase
- Adding unrelated infrastructure, UI, or controller surfaces

## Product Bar

- A new agent should be able to find the right doc path from `AGENTS.md`.
- A new operator should be able to run probe, prepare, and baseline flows from the runbook alone.
- A reviewer should be able to audit intent, architecture, and validation from repo-local files without external context.
