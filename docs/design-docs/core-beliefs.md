# Core Beliefs

This repo adopts the Harness-style rule that repository knowledge is the system of record. The goal is progressive disclosure: a short map up front, deeper docs where they belong.

## Beliefs

1. Repo-local knowledge beats prompt-local knowledge.
   If a constraint matters for future work, it belongs in versioned docs or code.

2. `AGENTS.md` is a map, not an encyclopedia.
   Keep root guidance short enough that agents still have room for the task, code, and relevant references.

3. One repo, one clear job.
   This project prepares, validates, and documents Modal runs for `karpathy/autoresearch`. Generic sandbox sprawl is a regression.

4. Plans are first-class artifacts.
   Active work, completed work, and debt belong in `docs/exec-plans/`, not in hidden side channels.

5. Generated docs must name their source.
   If a document is derived from code, it should point to that code and describe how to regenerate it.

6. Historical records should stay readable.
   Completed plans can preserve context, but broken links and stale path references should be repaired during migrations.

## Source

These beliefs are aligned to the repo-local knowledge guidance in OpenAI’s Harness engineering post: [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/).
