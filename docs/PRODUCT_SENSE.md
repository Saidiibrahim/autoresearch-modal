# Product Sense

## User Job

Give a human operator and coding agent a clear, repeatable way to run the upstream `autoresearch` research loop on Modal from a repo that already contains the required upstream files.

## Priority Order

1. Reproducibility of the Modal workflow
2. Faithfulness to the upstream human/agent contract
3. Clarity of repo-local guidance
4. Narrow scope and low cognitive overhead
5. Fast validation loops with exact commands
6. Historical traceability through plans and references

## Non-Goals

- Becoming a general-purpose agent sandbox
- Owning the upstream `karpathy/autoresearch` codebase
- Adding unrelated infrastructure, UI, or controller surfaces

## Product Bar

- A new agent should be able to find the right doc path from `AGENTS.md`.
- A new operator should be able to run probe, prepare, `program.md` edits, baseline smoke, and the agent loop from the runbook alone.
- A reviewer should be able to audit intent, architecture, and validation from repo-local files without external context.
