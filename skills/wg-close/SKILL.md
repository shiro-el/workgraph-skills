---
name: wg-close
description: Before a project branch merges into develop, check that the integrated code matches the Linear spec, file every gap as a new issue, and open the final project → develop PR for human review and merge. Use for $wg-close in Codex or /wg-close in Claude Code project when all project issues are Done.
---

# wg-close

Resolve `WORKGRAPH_ROOT` by resolving symlinks on this installed `SKILL.md`, then taking `../..` from its containing skill directory (the directory containing `conventions.md` and `vendor/`), never from the target repository or current working directory. Paths below use that resolved root; it is not a host-provided environment variable.

Read `${WORKGRAPH_ROOT}/conventions.md`, then adapt `${WORKGRAPH_ROOT}/vendor/spec-kit/templates/commands/analyze.md` (detection passes, severity, report shape). Overrides:

## Artifacts compared

Spec = the Linear project description. Plan = the `Architecture` document plus every project issue (including Canceled ones, with their reason). Implementation = the `project/<slug>` branch at its current head, in a fresh worktree. Ignore spec-kit's file paths, prerequisite scripts and constitution. Use the repo's CLAUDE.md / AGENTS.md in place of the constitution.

## Passes

1. **Verify the integrated branch.** Holding the check lane, run the full test suite, build and lint once on the integrated SHA and record them per conventions Verification runs; auditors cite that record. Then run every e2e row from every issue's Test design against the running app. Integration bugs hide between individually green PRs.
2. **Spec coverage.** For every requirement, acceptance criterion and edge case in the project description: the issue(s) that claimed it, the merged code and test that prove it, and the result (met / partial / missing / contradicted). Evidence is a test name plus a run, or a reproduction, never "looks implemented".
3. **Drift.** Find code behavior the spec never asked for, Architecture surfaces that changed, and `Decisions` / `Open questions` still open.

Run passes 2–3 with one claude and one codex auditor in parallel (read-only, own worktrees). Merge their tables, and judge disagreements by rerunning the evidence yourself.

## Output

- One comment on the Linear project (`save_status_update` or a project document named `Close audit`) with the coverage table, the drift list and the verification results.
- Each partial / missing / contradicted / drift item becomes a new Linear issue in the same project, in the conventions issue format with a risk Estimate. Ask the user first when an item is really a spec change rather than a bug.
- If nothing blocks: open the final PR `project/<slug>` → `develop` with the coverage table, integrated verification results, links to the merged issue PRs and their AI reviews, and any nonblocking Consider items in its body. Report it for human review and merge; do not merge it automatically. This is the project's routine human PR review checkpoint. If anything blocks, leave the PR unopened and list the blocking issues.
