---
name: run-workgraph
description: Coordinate a planned graph of software issues through parallel implementation, independent PR review, merge, and integration verification. Use when asked to execute a multi-PR goal.
---

# Run a work graph

You are the main coordinator. Begin from the approved or requested work graph and the user's actual completion condition. For a graph produced by `plan-workgraph`, run its `scripts/validate_workgraph.py <path-to-workgraph.yaml> --dispatch-ready` before scheduling or after topology changes. Check issue state and semantic conflicts yourself; the script only validates static structure. Keep a durable status record in the repository or issue tracker so another session can recover the state. Treat an active Goal as the overall outcome and evidence standard, not as a substitute for the work graph.

## Dispatch

- Release an item when prerequisites are satisfied and its contracts are stable enough to implement. Check conflict edges before parallel dispatch.
- Give **every subagent its own Git worktree**, including implementation, review, and integration audit agents. Never assign two agents the same worktree or have a reviewer check out an implementation branch already checked out elsewhere. An implementer uses its own branch; a reviewer can inspect the PR's pinned head in a detached worktree. Track the worktree path, owner, base/head revision, and cleanup state. Preserve uncommitted work when retiring a worktree.
- You alone decide whether to delegate, how many agents to run, and each agent's model and reasoning effort. Give each agent one bounded assignment, the relevant issue/spec, base revision, owned scope, expected result, and verification requirements.
- Choose model and effort from ambiguity, cross-module impact, failure cost, and observed rework. A clear local edit may use Luna at low or medium effort; coordination and ordinary coding may call for Luna medium or Sol medium; complex design, difficult debugging, or consequential review may justify Sol high or Astra. These are examples, not fixed routing rules. Respect the models actually available in the environment.
- Implementation agents use `implement-issue`; separate review agents use `review-issue-pr`. Neither role delegates further. Prefer a fresh reviewer context that has the issue and pinned PR diff, without the implementer's conclusions.

## Review and merge

- Treat the issue's acceptance criteria as the requirement source and the PR as evidence of what changed. Check the exact PR head revision reviewed; after code changes, request review of the new diff as warranted.
- Triage findings using concrete evidence. Send valid fixes to the implementation owner when useful. If the same substantive failure recurs, reassess the issue contract and raise model or effort rather than repeating an identical loop.
- Merge only work authorized by the user or active goal, after required review, relevant tests, and repository merge checks pass on the current target state. Respect dependency order. On busy branches, use the available merge queue or equivalent latest-base validation.
- Record PR URL, commit/head revision, checks, review outcome, merge state, and blockers. Keep claims of completion tied to evidence.

After the graph is merged, invoke `audit-integrated-work` for the combined result. Route confirmed integration defects into focused fixes and verify again. Finish only when the goal's completion condition is met or a concrete blocker is reported. Do not treat a green individual PR as proof that the overall goal is complete.
