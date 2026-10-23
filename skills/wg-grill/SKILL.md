---
name: wg-grill
description: First step of the workgraph pipeline. Interview the user relentlessly to turn a rough idea into settled decisions before any spec is written. Use for $wg-grill in Codex or /wg-grill in Claude Code, "grill me", or when a feature request is still vague.
---

# wg-grill

Resolve `WORKGRAPH_ROOT` by resolving symlinks on this installed `SKILL.md`, then taking `../..` from its containing skill directory (the directory containing `conventions.md` and `vendor/`), never from the target repository or current working directory. Paths below use that resolved root; it is not a host-provided environment variable.

Read `${WORKGRAPH_ROOT}/conventions.md`, then follow `${WORKGRAPH_ROOT}/vendor/mattpocock-skills/skills/productivity/grilling/SKILL.md` exactly, with these overrides:

- **Ground first.** Before round 1, read the Linear team's existing projects and issues that touch the same area (Linear MCP `list_projects`, `list_issues` with a `query`) and any related open issue the user named. Facts from Linear and the codebase are yours to find, never questions.
- **Sizing is a frontier question** in round 1: small (one PR) or large (a Linear project). Recommend one.
- **Always cover** these branches of the design tree before finishing: who the actors are, the happy path, every failure and refusal path, money/permissions/personal data, what is explicitly out of scope, and how a human will check it is done.
- **Output.** When the frontier is empty and the user confirms shared understanding, write nothing to the repo. Hand the settled decision list (each decision, the chosen answer, and the rejected alternatives) to `wg-spec` in the conversation.

**Override check.** After reading the upstream files and before acting on them, reread this file's overrides. Where upstream and these overrides or `conventions.md` differ, the overrides win; skip the upstream parts they replace instead of reconciling them.
