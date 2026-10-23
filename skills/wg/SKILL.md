---
name: wg
description: Entry point and coordinator of the Linear-driven workgraph pipeline. Routes an idea through grill → spec → (architect → plan) → implement → cross-model review → close, and dispatches ready Linear issues to implementer subagents in their own worktrees. Resumable from Linear state. Use for $wg in Codex or /wg in Claude Code idea | ISSUE-ID | project.
---

# wg

Resolve `WORKGRAPH_ROOT` by resolving symlinks on this installed `SKILL.md`, then taking `../..` from its containing skill directory (the directory containing `conventions.md` and `vendor/`), never from the target repository or current working directory. Paths below use that resolved root; it is not a host-provided environment variable.

Read `${WORKGRAPH_ROOT}/conventions.md` first. Linear is the state. Reread it on every start instead of trusting memory, so any session can pick up the work; start from the project's latest `Handover` comment if there is one, then confirm it against current Linear and GitHub state.

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

0. **Preflight (once per session).** Before the first dispatch, check every environment dependency the ready issues' Test design needs and fix what you can: `gh` and Linear access, a smoke prompt for each model CLI (conventions CLI assignments), the container engine when tests need a local DB, the repo's runtime version, line endings of the checkout the tests run in, env vars reaching the process that actually runs the tests (print them from inside it, e.g. across WSL → Windows), the browser tool opening a page, and test accounts signing in (including MFA). Ask the user once, as one list, for whatever you cannot fix. Record the result as a Linear project comment.
1. **Branch (large, once).** If `project/<slug>` does not exist, create it from `develop` and push it.
2. **Ready set** = issues in `Todo` whose blockers are all `Done` and that do not carry `needs-human`. An issue blocked by an `interface` issue waits until that PR has passed AI review and merged into the project branch.
3. **Parallelism.** Run ready issues in parallel only when their `Files likely touched` don't overlap. Otherwise run them one after another.
4. **Implement.** One implementer subagent per issue (`Agent`, `general-purpose`, `isolation: "worktree"`, `run_in_background: true`) told to follow `${WORKGRAPH_ROOT}/skills/wg-implement/SKILL.md`. The default author model is the current host family (`codex` in Codex, `claude` in Claude Code); apply the conventions host compatibility rules. Record the author model: the review roster depends on it.
   `isolation: "worktree"` only works when this session's cwd is the target repo. Otherwise create the worktree yourself before spawning (`git -C <repo> fetch origin` then `git -C <repo> worktree add <tmp>/wt-<ISSUE-ID> -b <gitBranchName> origin/<base>`), drop `isolation`, and give the implementer that absolute path as the only place it may edit. Remove it with `git worktree remove` once the PR is merged or abandoned.
5. **Pre-PR checks.** When an implementer reports a pushed branch, spawn the e2e verifier and the pre-review described in `wg-implement`, each in its own worktree. Send the findings back to the implementer with `SendMessage`. Repeat until it opens the PR.
   A defect outside the issue's acceptance criteria (pre-existing, another layer, another screen) is not fixed silently in this PR. If it blocks an acceptance criterion or an e2e row, stop and ask the user: widen this issue (amend its spec and Test design per `wg-spec`, then continue) or file a new issue that `blocks` this one. Otherwise file a new Linear issue with the reproduction and continue. Record the choice as an issue comment.
6. **Review.** For each opened PR, run `wg-review`. You spawn its reviewers (your subagents and `codex exec` calls), which write findings to temp files; a lead-judge subagent synthesizes, posts and returns only the verdict (wg-review "Lead judge"). Raw findings never enter your context.
7. **Merge or hand off.** When an intermediate issue PR passes review, merge it into `project/<slug>` under the conventions PR review and merge rules. Do not ask the user to review or approve each intermediate PR. Confirm the merge and wait for the GitHub integration to move the issue to `Done`, then recompute the ready set and continue dispatch. On resume, an already-passed PR can proceed to merge only after rechecking those conditions. For a small issue's final PR to `develop`, report it for human review and merge instead.
8. **Finish or stop.** When all project issues are `Done` / `Canceled`, continue directly to `wg-close` for the integrated audit and final PR; you dispatch its verifier, auditors and judge as subagents, as in `wg-close`. Otherwise, when nothing is ready or running, report: merged, awaiting final human review and merge, `needs-human` (with the reason), still blocked, or awaiting GitHub status synchronization.

## Coordinator rules

- Choose each subagent's model and effort from risk (the Estimate) and observed rework. A same-shape failure twice means raising effort or reassessing the issue, not a third identical try.
- Every subagent gets one bounded assignment in the conventions handoff format, and reports back in it.
- Keep your context small. Subagents return conclusions and evidence summaries, not file dumps.
- **Shift handover.** After every 5 merges, or sooner when your context is long or you notice yourself rereading earlier results, stop dispatching new work, wait for running subagents, and post a Linear project comment headed `Handover`: issues by status, open PRs with their reviewed SHA and round, check-lane holder, `needs-human` reasons, and the next action. Then tell the user to resume in a fresh session with `wg <project>`. Linear is the state; the handover comment only saves the next session a reread.
- **Metrics.** When an issue PR merges or an issue stops on `needs-human`, record its conventions work metrics as an issue comment. Use them when choosing model and effort.
- You dispatch, grant the check lane (conventions Verification runs), merge and update Linear. You do not implement, verify or run suites yourself: anything longer than a quick status query goes to a subagent, including rebasing a branch onto a newly merged base and rerunning its checks.
- Wait on completion events (the host's agent wait tool or task notifications), not `sleep` loops or log tailing.
