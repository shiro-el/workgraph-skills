---
name: review-issue-pr
description: Independently review one PR against its issue, repository standards, and verification evidence. Use when assigned a PR review in a multi-PR workflow.
---

# Review one issue PR

Work in your own dedicated Git worktree. Inspect the PR at a pinned head revision, preferably with a detached checkout so the implementer's branch remains in its worktree. Read the originating issue and its acceptance criteria, the repository's relevant standards, the PR diff, and available test results. Do not treat the PR description as a replacement for the issue. Inspect surrounding code where needed to judge behavior and impact.

Assess separately:

1. **Spec:** missing, partial, or incorrect behavior; important edge cases; unrequested scope.
2. **Code:** correctness, maintainability, contract compatibility, and documented repository rules.
3. **Evidence:** whether tests and other checks actually support the claimed result.

Report actionable findings with file/line or another precise location, affected requirement or rule, concrete failure mode, severity, and a way to verify the fix. Distinguish confirmed defects from risks or design preferences. State which checks you ran yourself and which results you only read. If evidence is insufficient, say exactly what is missing.

Return a concise recommendation for this pinned revision: ready, changes needed, or unable to verify. The coordinator owns the merge decision. Review the new head revision after assigned fixes; do not rely on a prior recommendation for changed code.

Do not spawn subagents, edit implementation code, approve your own work, or merge the PR.
