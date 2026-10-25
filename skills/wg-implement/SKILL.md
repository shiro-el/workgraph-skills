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
- Commit each row's test alone once it fails for the intended reason (`test(<ISSUE-ID>): RED <row>`), before any production code for that row. From then on that test is locked: GREEN and REFACTOR commits do not touch it. A locked test that turns out wrong may be changed only in its own commit, listed under the PR's `Test changes after RED` with the commit SHA and why; never weaken an assertion to get to green.
- A row you find impossible or wrong is not silently dropped: note it in the PR's evidence with the reason.
- Implement against the Architecture sketch as in `${WORKGRAPH_ROOT}/vendor/cursor-plugins/pstack/skills/architect/SKILL.md` Phase D. A needed deviation (new parameter, changed type, moved boundary) on an `interface`-defined surface stops you: comment on the issue with the deviation and why, add `needs-human`, and report. Repeated same-shape friction is Phase E's scrap signal: report it rather than patching around it.
- Follow the repo's CLAUDE.md / AGENTS.md and existing patterns, per feature-dev phase 5.

## Before the PR (coordinator-run checks)

When all rows pass and the changed-files check is green (conventions Verification runs; the full suite waits for the SHA that passes review), push the branch and report to the coordinator in the conventions handoff format: branch, head SHA, the recorded verification runs for that SHA (conventions Verification runs), how to run the app, which screens changed. Subagents cannot spawn subagents, so the coordinator (`wg`) runs these in their own worktrees and sends you the results:

- **e2e verifier**: drives the real app in a real browser per `${WORKGRAPH_ROOT}/vendor/addyosmani-agent-skills/skills/browser-testing-with-devtools/SKILL.md`, runs the issue's e2e rows, and for frontend changes captures screenshots of each changed state at desktop and mobile width as separate native-resolution files (conventions Evidence rule).
- **pre-review**: one `code-reviewer` pass (`${WORKGRAPH_ROOT}/vendor/claude-code/plugins/feature-dev/agents/code-reviewer.md`) on the model you are not.

Fix confirmed findings under the evidence rule, then open the PR.

## Open the PR

`gh pr create` against the base branch, title = issue title, body:

```markdown
Linear: [<ISSUE-ID> <issue title>](<issue URL>)

Closes <ISSUE-ID>
Author-model: <claude|codex> (<effort>)

## What changed
## Test design coverage
| Row | Test | RED commit | Before (fail output, trimmed) | After |
## Test changes after RED
<one row per commit that edits a locked test: SHA, test, why; "none" if none>
## Verification
<one row per run: SHA, command, environment, result, duration — focused tests, full suite, build, lint, e2e>
## Screenshots
<link to the Linear `## Screenshots` comment, then one line per state and width>
## Deviations / notes
```

`Author-model` is your model family and effort as the coordinator assigned them; the review roster reads it. Put the screenshots inline in one Linear issue comment as the conventions Evidence rule says (one native-resolution file per state and width, `prepare_file_upload`, never stitched, never Resources) and link that comment. Never commit them. For a final PR to `develop` (small work), which gets no review panel, put the `Linear:` line first, then the `## Review guide` and `## Where the automation is least sure` sections shaped as in `wg-close` Output, scoped to this PR, and run the full suite on the head SHA as in "During review". Set the issue to `In Review`, then report the PR URL and head SHA to the coordinator.

## During review

You receive confirmed findings from `wg-review`. For each one: reproduce it, then grep for every place that shares the defective pattern (sibling writers, the other half of a read/write pair, the same rule duplicated in SQL and app code) and fix all of them in the same push, test-first (failing-before → passing-after) for each, with the same RED commit and test lock. Push, and reply on the PR thread with the evidence and the list of places checked. If you dispute a finding, reply with counter-evidence instead of changing code.

When the coordinator reports that review passed, run the full suite on that head SHA holding the check lane, add it to the PR's Verification section and report the result. A failure is fixed like a finding: test-first, push, and the new SHA goes back to review.

**Override check.** After reading the upstream files and before acting on them, reread this file's overrides. Where upstream and these overrides or `conventions.md` differ, the overrides win; skip the upstream parts they replace instead of reconciling them.
