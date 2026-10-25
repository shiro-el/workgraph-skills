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
| large: plan done, a project issue still in `Backlog` | complete it to `Todo` or add `needs-human` (conventions Status flow), then route again |
| all project issues `Done` / `Canceled` | `wg-close` |
| final PR with unaddressed human review comments | large: file each as a project issue (a spec change goes through `wg-spec` first), dispatch them, then `wg-close` again on the new head; small: send them to the implementer as findings (`wg-implement` "During review"), then report the new head for human review |
| small: a single issue in `Todo` | Dispatch loop, with that one issue |

Stop between grill/spec/architect/plan for the user's approval. From dispatch onward, run without stopping except where `needs-human` says so.

## Dispatch loop

0. **Preflight (once per session).** If the project has a preflight comment from this machine in the last 24 hours, reuse it and rerun only the CLI smoke prompts and the leftover sweep. Otherwise, before the first dispatch, check every environment dependency the ready issues' Test design needs and fix what you can: `gh` and Linear access, a smoke prompt for each model CLI (conventions CLI assignments), the container engine when tests need a local DB, the repo's runtime version, line endings of the checkout the tests run in, env vars reaching the process that actually runs the tests (print them from inside it, e.g. across WSL → Windows), the browser tool opening a page, and test accounts signing in (including MFA). Leftover sweep: for each `git worktree list` entry named `wg-*` whose issue is `Done` / `Canceled` or whose assignment no longer runs, apply the conventions Cleanup rule, and release the repo's per-worktree resources (DB slots and the like) that no remaining worktree owns. Ask the user once, as one list, for whatever you cannot fix. Record the result as a Linear project comment.
1. **Branch (large, once).** If `project/<slug>` does not exist, create it from `develop` and push it.
2. **Ready set** = issues in `Todo` whose blockers are all `Done` and that do not carry `needs-human`. An issue blocked by an `interface` issue waits until that PR has passed AI review and merged into the project branch. On resume, an issue in `In Progress` with no running implementer and no PR goes back to `Todo` if its branch has no commits; otherwise dispatch an implementer to continue on that branch.
3. **Parallelism.** Run ready issues in parallel only when their `Files likely touched` don't overlap. Otherwise run them one after another.
4. **Implement.** One implementer subagent per issue (`Agent`, `general-purpose`, `isolation: "worktree"`, `run_in_background: true`) with description `wg-impl-<ISSUE-ID>` (conventions agent labels), told to follow `${WORKGRAPH_ROOT}/skills/wg-implement/SKILL.md`. The default author model is the current host family (`codex` in Codex, `claude` in Claude Code); apply the conventions host compatibility rules. Tell the implementer its model family and effort; it writes them in the PR body's `Author-model:` line, which the review roster reads.
   `isolation: "worktree"` only works when this session's cwd is the target repo. Otherwise create the worktree yourself before spawning (`git -C <repo> fetch origin` then `git -C <repo> worktree add <tmp>/wg-impl-<ISSUE-ID> -b <gitBranchName> origin/<base>`), drop `isolation`, and give the implementer that absolute path as the only place it may edit. Either way, remove the worktree and its DB slot and other per-worktree resources when the PR merges or is abandoned (conventions Worktrees and branches, Cleanup).
5. **Pre-PR checks.** When an implementer reports a pushed branch, spawn the e2e verifier and the pre-review described in `wg-implement`, each in its own worktree, labeled `wg-e2e-<ISSUE-ID>-<k>` and `wg-pre-<ISSUE-ID>-<k>` for pre-PR round `k`. Send the findings back to the implementer with `SendMessage`. After each round, post an issue comment starting with `<!-- wg:prepr wg=<version> sha=<SHA> round=<k> open=<confirmed findings left> reviewer=<model> -->`; count rounds from the latest marker, not from memory. Repeat until it opens the PR; if the third pre-PR round still has confirmed findings, add `needs-human` instead of a fourth.
   A defect outside the issue's acceptance criteria (pre-existing, another layer, another screen) is not fixed silently in this PR. If it blocks an acceptance criterion or an e2e row, stop and ask the user: widen this issue (amend its spec and Test design per `wg-spec`, then continue) or file a new issue that `blocks` this one. Otherwise file a new Linear issue with the reproduction (conventions Status flow: mid-run issues) and continue. Record the choice as an issue comment.
6. **Review.** For each opened intermediate PR, run `wg-review`. You spawn its reviewers (your subagents, and `codex exec` as your own background shell commands, never inside a wrapper subagent), which write findings to temp files; a lead-judge subagent synthesizes, posts and returns only the verdict (wg-review "Lead judge"). Raw findings never enter your context.
7. **Merge or hand off.** When an intermediate issue PR passes review, merge it into `project/<slug>` under the conventions PR review and merge rules. Do not ask the user to review or approve each intermediate PR. Confirm the merge, post one line as a Linear project status update (issue merged, its Consider count, issues left), and wait for the GitHub integration to move the issue to `Done`, then recompute the ready set and continue dispatch. On resume, an already-passed PR can proceed to merge only after rechecking those conditions; its latest `wg:review` marker (wg-review "Post") must say `verdict=pass` for the current head SHA. A small issue's final PR to `develop` skips step 6: have the implementer run the full suite on its head (`wg-implement` "Open the PR"), then report it for human review and merge with the conventions Work metrics workload rating request; leave the issue `In Review` until the merge integration moves it to `Done`.
8. **Finish or stop.** When all project issues are `Done` / `Canceled`, continue directly to `wg-close` for the integrated audit and final PR; you dispatch its verifier, auditors and judge as subagents, as in `wg-close`. Report each new `needs-human` to the user as soon as it is set, with its question, the options and their consequences, your recommendation, and how to resume (conventions Labels). Otherwise, when nothing is ready or running, report: merged, awaiting final human review and merge, `needs-human` (with the reason), still blocked, or awaiting GitHub status synchronization.

## Coordinator rules

- Choose each subagent's model and effort from risk (the Estimate) and observed rework. A same-shape failure twice means raising effort or reassessing the issue, not a third identical try.
- Every subagent gets one bounded assignment in the conventions handoff format, and reports back in it.
- Keep your context small. Subagents return conclusions and evidence summaries, not file dumps.
- **Shift handover.** When 5 PRs have merged since the latest `Handover` comment (count them with `gh`, not from memory), or sooner when your context is long, stop dispatching new work, wait for running subagents, and post a Linear project comment headed `Handover`: issues by status, open PRs with their reviewed SHA, round and author model, issues still in pre-PR checks with their latest `wg:prepr` round, worktrees you created yourself (path and issue), `needs-human` reasons, and the next action. Then tell the user, starting with "Paused: nothing is running", to resume in a fresh session with `wg <project>`. Linear is the state; the handover comment only saves the next session a reread.
- **Metrics.** When an issue PR merges or an issue stops on `needs-human`, post its conventions `wg:metrics` marker as an issue comment.
- You dispatch, merge and update Linear. Subagents take the check lane themselves (conventions Verification runs). You do not implement, verify or run suites yourself: anything longer than a quick status query goes to a subagent, including rebasing a branch onto a newly merged base and rerunning its checks.
- Wait on completion events (the host's agent wait tool or task notifications), not `sleep` loops or log tailing. This applies to you only: every assignment you hand a subagent, and any driver file you write for one, carries the conventions rule for waiting inside an assignment, so it never stops just to wait.
