---
name: wg-grill
description: First step of the workgraph pipeline. Interview the user relentlessly to turn a rough idea into settled decisions before any spec is written. Use for /wg-grill, "grill me", or when a feature request is still vague.
---

# wg-grill

Read `${CLAUDE_PLUGIN_ROOT}/conventions.md`, then follow `${CLAUDE_PLUGIN_ROOT}/vendor/mattpocock-skills/skills/productivity/grilling/SKILL.md` exactly, with these overrides:

- **Ground first.** Before round 1, read the Linear team's existing projects and issues that touch the same area (Linear MCP `list_projects`, `list_issues` with a `query`) and any related open issue the user named. Facts from Linear and the codebase are yours to find, never questions.
- **Sizing is a frontier question** in round 1: small (one PR) or large (a Linear project). Recommend one.
- **Always cover** these branches of the design tree before finishing: who the actors are, the happy path, every failure and refusal path, money/permissions/personal data, what is explicitly out of scope, and how a human will check it is done.
- **Output.** When the frontier is empty and the user confirms shared understanding, write nothing to the repo. Hand the settled decision list (each decision, the chosen answer, and the rejected alternatives) to `wg-spec` in the conversation.
