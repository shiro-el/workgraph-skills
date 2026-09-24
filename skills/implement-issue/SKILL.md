---
name: implement-issue
description: Implement one assigned software issue and submit a scoped PR with verification evidence. Use for an implementation assignment from a multi-PR coordinator.
---

# Implement one issue

Use the assigned issue and acceptance criteria as the requirement source. Work only in the dedicated Git worktree assigned to you; verify its path, branch, base revision, owned scope, and interface assumptions before editing. Do not change another agent's worktree. If an assumption remains unresolved, make the most defensible bounded choice and report it; tell the coordinator promptly when it would change another worker's contract.

Implement the smallest coherent change that satisfies the issue. Add or update meaningful tests for changed behavior and run the relevant checks. Inspect your own diff for obvious mistakes, accidental scope changes, and generated or shared-file edits. This self-check is part of implementation; it is not independent approval.

When PR creation is part of the assignment, open a PR linked to the issue. Describe the change, verification performed, any unverified behavior, and contract decisions that affect other items. Return the PR URL, head revision, tests and results, assumptions, and remaining blockers to the coordinator.

Do not spawn subagents, invoke an independent review skill, approve your own PR, or merge it. Address review feedback assigned by the coordinator in the same branch when appropriate, then report the new head revision and checks.
