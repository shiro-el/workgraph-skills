---
name: wg-implement
description: Implement one Linear issue test-first in its own git worktree, then open a PR that carries the evidence. Run as the implementer subagent dispatched by wg, or directly for a single small issue. Use for $wg-implement in Codex or /wg-implement in Claude Code ISSUE-ID.
---

# wg-implement

Resolve `WORKGRAPH_ROOT` by resolving symlinks on this installed `SKILL.md`, then taking `../..` from its containing skill directory (the directory containing `conventions.md` and `vendor/`), never from the target repository or current working directory. Paths below use that resolved root; it is not a host-provided environment variable.

Read `${WORKGRAPH_ROOT}/conventions.md` first. You own exactly one Linear issue.

## Setup

1. Read the issue (`get_issue` with relations), its project description, and the project's `Architecture` document if there is one. The acceptance criteria and Test design are the requirement. The Architecture slice is the contract.
2. If any blocker issue is not `Done`, stop and report.
3. Create a worktree on the issue's `gitBranchName`, based on `project/<project-slug>` (large) or `develop` (small). If the coordinator already gave you a worktree path, use it and work nowhere else. Set the issue to `In Progress`.

## Build test-first

Follow `${WORKGRAPH_ROOT}/vendor/addyosmani-agent-skills/skills/test-driven-development/SKILL.md`, including "Discover the Stack First". Overrides:

- Work through the issue's Test design table row by row: RED (run it, save the failing output), GREEN (smallest change), REFACTOR. Do not write production code for a row before its test has failed for the intended reason.
- A row you find impossible or wrong is not silently dropped: note it in the PR's evidence with the reason.
- Implement against the Architecture sketch as in `${WORKGRAPH_ROOT}/vendor/cursor-plugins/pstack/skills/architect/SKILL.md` Phase D. A needed deviation (new parameter, changed type, moved boundary) on an `interface`-defined surface stops you: comment on the issue with the deviation and why, add `needs-human`, and report. Repeated same-shape friction is Phase E's scrap signal: report it rather than patching around it.
- Follow the repo's CLAUDE.md / AGENTS.md and existing patterns, per feature-dev phase 5.

## Before the PR (coordinator-run checks)

When all rows pass and the full relevant suite is green, push the branch and report to the coordinator: branch, head SHA, how to run the app, which screens changed. Subagents cannot spawn subagents, so the coordinator (`wg`) runs these in their own worktrees and sends you the results:

- **e2e verifier**: drives the real app in a real browser per `${WORKGRAPH_ROOT}/vendor/addyosmani-agent-skills/skills/browser-testing-with-devtools/SKILL.md`, runs the issue's e2e rows, and for frontend changes captures screenshots of each changed state at desktop and mobile width.
- **pre-review**: one `code-reviewer` pass (`${WORKGRAPH_ROOT}/vendor/claude-code/plugins/feature-dev/agents/code-reviewer.md`) on the model you are not.

Fix confirmed findings under the evidence rule, then open the PR.

## Open the PR

`gh pr create` against the base branch, title = issue title, body:

```markdown
Closes <ISSUE-ID>

## What changed
## Test design coverage
| Row | Test | Before (fail output, trimmed) | After |
## Verification
<commands run and their results: focused tests, full suite, build, lint, e2e>
## Screenshots
<Linear attachment links, one per state and width>
## Deviations / notes
```

Upload screenshots to the Linear issue (`prepare_attachment_upload` → `create_attachment_from_upload`) and link them. Never commit them. Set the issue to `In Review`, then report the PR URL and head SHA to the coordinator.

## During review

You receive confirmed findings from `wg-review`. For each one: reproduce it, then grep for every place that shares the defective pattern (sibling writers, the other half of a read/write pair, the same rule duplicated in SQL and app code) and fix all of them in the same push, test-first (failing-before → passing-after) for each. Push, and reply on the PR thread with the evidence and the list of places checked. If you dispute a finding, reply with counter-evidence instead of changing code.
