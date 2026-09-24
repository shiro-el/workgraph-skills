---
name: audit-integrated-work
description: Verify that a multi-PR software goal works as an integrated whole after its changes merge. Use for final cross-issue verification and integration review.
---

# Audit the integrated result

Use your own dedicated Git worktree at the current target revision. Read the original goal, work graph, and merged issues/PRs. Confirm which changes actually landed. Review the combined behavior rather than repeating every PR's local review.

Focus on cross-issue contracts, end-to-end user flows, migration or rollout order, shared configuration, error handling across boundaries, and requirements that no single issue owned. Run the relevant integration checks and inspect their results. Choose deeper checks according to the changed system and the goal's evidence standard.

For each finding, identify the affected requirement or flow, observed or plausible failure, supporting evidence, and the smallest useful repair scope. Distinguish defects from unverified risks. Report the current target revision, checks, results, and whether the goal's completion condition is met.

Do not spawn subagents or merge fixes. Return confirmed work to the coordinator for focused repair and re-verification.
