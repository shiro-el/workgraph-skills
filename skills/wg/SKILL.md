---
name: wg
description: Entry point and coordinator of the Linear-driven workgraph pipeline. Routes an idea through grill → spec → (architect → plan) → implement → cross-model review → close, and dispatches ready Linear issues to implementer subagents in their own worktrees. Resumable from Linear state. Use for $wg in Codex or /wg in Claude Code idea | ISSUE-ID | project.
---

# wg

Resolve `WORKGRAPH_ROOT` by resolving symlinks on this installed `SKILL.md`, then taking `../..` from its containing skill directory (the directory containing `conventions.md` and `vendor/`), never from the target repository or current working directory. Paths below use that resolved root; it is not a host-provided environment variable.

Read `${WORKGRAPH_ROOT}/conventions.md` first. Linear is the state. Reread it on every start instead of trusting memory, so any session can pick up the work.

## Route

| Input | Next |
|---|---|
| a new idea | `wg-grill` → `wg-spec` |
| project or issue with `## Spec review` set to `Pending` | `wg-spec` (resume the HTML review from the Linear draft) |
| large: project in `Backlog` without an `Architecture` document | `wg-architect` |
| large: architecture approved, no issues yet | `wg-plan` |
| issues in `Todo` / `In Progress` / `In Review` | Dispatch loop below |
| all project issues `Done` / `Canceled` | `wg-close` |
| small: a single issue in `Todo` | Dispatch loop, with that one issue |

Stop between grill/spec/architect/plan for the user's approval. From dispatch onward, run without stopping except where `needs-human` says so.

## Dispatch loop

1. **Branch (large, once).** If `project/<slug>` does not exist, create it from `develop` and push it.
2. **Ready set** = issues in `Todo` whose blockers are all `Done` and that do not carry `needs-human`. An issue blocked by an `interface` issue waits until that PR is merged by a human.
3. **Parallelism.** Run ready issues in parallel only when their `Files likely touched` don't overlap. Otherwise run them one after another.
4. **Implement.** One implementer subagent per issue (`Agent`, `general-purpose`, `isolation: "worktree"`, `run_in_background: true`) told to follow `${WORKGRAPH_ROOT}/skills/wg-implement/SKILL.md`. The default author model is the current host family (`codex` in Codex, `claude` in Claude Code); apply the conventions host compatibility rules. Record the author model: the review roster depends on it.
   `isolation: "worktree"` only works when this session's cwd is the target repo. Otherwise create the worktree yourself before spawning (`git -C <repo> fetch origin` then `git -C <repo> worktree add <tmp>/wt-<ISSUE-ID> -b <gitBranchName> origin/<base>`), drop `isolation`, and give the implementer that absolute path as the only place it may edit. Remove it with `git worktree remove` once the PR is merged or abandoned.
5. **Pre-PR checks.** When an implementer reports a pushed branch, spawn the e2e verifier and the pre-review described in `wg-implement`, each in its own worktree. Send the findings back to the implementer with `SendMessage`. Repeat until it opens the PR.
   A defect outside the issue's acceptance criteria (pre-existing, another layer, another screen) is not fixed silently in this PR. If it blocks an acceptance criterion or an e2e row, stop and ask the user: widen this issue (amend its spec and Test design per `wg-spec`, then continue) or file a new issue that `blocks` this one. Otherwise file a new Linear issue with the reproduction and continue. Record the choice as an issue comment.
6. **Review.** For each opened PR, run `wg-review` (you drive it; the reviewers are your subagents and `codex exec` calls).
7. **Hand off.** When a review passes, report the PR to the user for merging. Agents never merge. Merged PRs move issues to `Done` through the GitHub integration. Then recompute the ready set.
8. **Stop** when nothing is ready or running. Report: merged, awaiting human merge, `needs-human` (with the reason), still blocked. A human merge unblocks the next `wg` run.

## Coordinator rules

- Choose each subagent's model and effort from risk (the Estimate) and observed rework. A same-shape failure twice means raising effort or reassessing the issue, not a third identical try.
- Every subagent gets one bounded assignment: the issue ID, its base SHA, its worktree, the expected output, and the evidence rule.
- Keep your context small. Subagents return conclusions and evidence summaries, not file dumps.
