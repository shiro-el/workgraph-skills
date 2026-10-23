# Workgraph conventions

Every `wg-*` skill follows these rules. Upstream skills live verbatim under `${WORKGRAPH_ROOT}/vendor/` (pinned git submodules). When an upstream file and this file disagree, this file wins.

## Host compatibility (Codex and Claude Code)

`WORKGRAPH_ROOT` is the installed plugin root, resolved from the selected skill's `SKILL.md` as described there. Read upstream files from that root, while running code and git commands in the target repository/worktree. If `vendor/` is missing, stop and initialize the clone's submodules (`git submodule update --init --recursive`); do not invent upstream instructions. These conventions and the stage's overrides take precedence over upstream host-specific instructions.

Invoke stages as `$wg` / `$wg-spec` in Codex or `/wg` / `/wg-spec` in Claude Code; the same files serve both hosts. A reference to another stage means read its `skills/<stage>/SKILL.md` under `WORKGRAPH_ROOT`.

- **Delegation:** `Agent`, `general-purpose`, `run_in_background`, and `SendMessage` in stage instructions describe Claude Code operations. In Codex, use the available native agent spawn, message, and wait tools for the equivalent bounded assignment. Create each worktree explicitly and pass its absolute path; Claude's `isolation: "worktree"` is not a Codex option. Use only capabilities exposed by the current host. If delegation is unavailable, run independent assignments sequentially through the required model's CLI, retaining separate worktrees and prompts.
- **Model identity:** a native subagent belongs to the current host's model family. Codex native agents are `codex`; Claude Code native agents are `claude`. Never label a native Codex agent as Claude. The default implementer uses the current host's family; record the actual author family for every issue.
- **Other family:** from Codex, run Claude assignments using an authenticated `claude` CLI in the assigned worktree with a prompt file, for example `(cd "<worktree>" && claude -p < "<tmp>/prompt.md" > "<tmp>/result.md")`. From Claude Code, use `codex exec` as below. Pass the full upstream prompt body and task context to either CLI; referring to a Claude agent name does not load it in Codex. Keep the CLI's normal permission controls.
- **Required capabilities:** discover the connected Linear tools and map the operation names in these instructions to their exposed equivalents. Read stages need Linear access; PR stages also need authenticated `gh`. Cross-model stages require both authenticated model families and review/e2e stages need their specified test/browser tools. If a required capability is missing, report exactly what is unavailable and stop that stage; do not silently replace a cross-model panel with one family or claim checks passed.

## Linear is the only document store

Never write specs, plans, task lists, ADRs, design notes or review reports into the code repository (`docs/`, `tasks/`, `specs/`, `plan.md`, …). Upstream skills that say "save to a file" save to Linear instead:

| Artifact | Large work | Small work |
|---|---|---|
| Spec (what and why) | Linear **project** description | Linear **issue** description |
| Architecture (types, signatures, boundaries, rationale) | Linear **document** named `Architecture` attached to the project | `## Design` section of the issue |
| Task | Linear **issue** in the project | the same single issue |
| Prerequisite DAG | issue `blocks` / `blockedBy` relations | — |
| Test design | `## Test design` section of each issue | same |
| Implementation evidence | GitHub PR body (Linear links it automatically) | same |
| Review findings | GitHub PR review comments | same |
| Leftover work | new Linear issues in the same project | new issues |

Code comments stay limited to the why the code cannot show. A scratch file needed during work goes under the OS temp dir, never the repo.

`wg-spec` uses html-plan pages as temporary review snapshots of the Linear draft. Keep their HTML and assets under the OS temp dir. Record review decisions, rationale and open questions in Linear; later stages resume from Linear without needing the page. `## Spec review` is `Pending` during review and `Complete` once the user's feedback is reflected in the spec. Pending drafts stay in `Backlog` and return to `wg-spec` before architecture or implementation.

## Sizing

- **Large** = one Linear project. Needs `wg-architect` and `wg-plan`; issues merge into `project/<project-slug>`; the project branch merges into `develop` only after `wg-close`.
- **Small** = one Linear issue, no project branch. Skip `wg-architect` and `wg-plan`; the PR targets `develop`.

When unsure, ask once: "does this need more than one PR?" Yes → large.

## Issue format

Use the team's `feat` / `bug` / `refactor` template headings, then add:

```markdown
## Background
## Scope
## Acceptance criteria
- [ ] …
## Test design
| # | Level (unit/integration/e2e) | Given | When | Then | Edge case? |
## Out of scope
```

Every acceptance criterion maps to at least one Test design row. Edge cases (empty, max, duplicate, concurrent, unauthorized, partial failure, retry/idempotency, time/zone, i18n) are rows, not prose.

## Status flow (team statuses, no extra labels)

`Backlog` draft → `Todo` spec complete, may be dispatched → `In Progress` implementer working → `In Review` PR open → `Done` (set by the GitHub integration when the PR merges).

## PR review and merge

- Every issue PR still runs `wg-review` and its fix → re-review loop.
- **Intermediate PRs** target the large project's `project/<slug>` branch. After review passes, the `wg` coordinator merges them without a per-PR human review or approval, including `interface` PRs. Reviewers and implementers report their results to the coordinator; they do not merge.
- Before merging, verify that the PR still targets the intended project branch, its head SHA matches the passed review, required CI checks have passed, and GitHub permits merging. Merge with `gh pr merge --match-head-commit <reviewed-SHA>` using the repository's supported merge method. A changed head needs review again; changes made to resolve conflicts also rerun the relevant checks and review. Never bypass branch protection or use an admin override. If a repository rule requires human approval or another merge condition cannot be satisfied, report the blocker with `needs-human`.
- **Final PRs** require human review and merge. For large work this is `project/<slug>` → `develop`, opened by `wg-close` after its integrated audit passes. For small work the single issue PR → `develop` is already the final PR. Agents leave these open for the user.
- Routine intermediate merges do not pause dispatch. Existing `needs-human` stops for unresolved findings, design changes and other exceptional blockers still apply.

## Labels

- `needs-human`: the pipeline stopped and waits for a person; the latest issue comment says why and what answer unblocks it. The person removes the label to resume.
- `interface`: the issue lands architect-defined types, signatures or schemas that other issues build on. Its PR must pass AI review and merge into the project branch before any blocked issue starts; no separate human merge is required.

Plus the existing type labels (`Feature`, `Bug`, `Improvement`).

## Risk = Estimate = reviewer count

The issue **Estimate** is its risk, not its effort. `wg-plan` sets it on every issue.

- reviewer count `n = min(estimate, 5)`; no estimate → stop and set one.
- Raise the estimate for: money, auth/permissions, personal data, migrations, concurrency, public API/`interface` issues, anything irreversible.

## Cross-model reviewer roster

Models: `claude` and `codex`, run through the host compatibility rules above. Let `A` be the model that wrote the code and `B` the other one. For review round `r` (1-based):

- majority = `B` when `r` is odd, `A` when `r` is even; majority size `ceil(n/2)`, minority `floor(n/2)`.
- n=1 → r1: B, r2: A, r3: B …
- n=2 → 1 B + 1 A every round.
- n=3 → r1: 2 B + 1 A, r2: 2 A + 1 B, …

Focuses, assigned in this order (reviewer i gets focus i; with n=1 the single reviewer takes focuses 1 and 2 together). Shift the focus list by one each round so each focus meets a different model:

1. Spec conformance: every acceptance criterion and Test design row is implemented and actually tested.
2. Correctness: bugs and logic errors in the introduced code.
3. Security and data integrity: authz, injection, PII exposure, money, idempotency, races, migrations.
4. Project conventions: CLAUDE.md / AGENTS.md rules that apply to the touched paths, quoted exactly.
5. Simplicity: dead code, duplication, needless abstraction, comments that restate code.

Running a codex reviewer (read-only, in the reviewer's own detached worktree):

```sh
codex exec -s read-only -C "<worktree>" -o "<tmp>/review-<i>.md" - < "<tmp>/prompt-<i>.md"
```

Keep the configured sandbox and permission controls on every host. If a sandbox prevents a required reproduction, report the limitation rather than changing to unrestricted access. Reviewers must not edit repository files. Check `git -C "<worktree>" status --porcelain` afterwards; discard results from an unexpectedly dirty worktree.

Running a Claude reviewer: use a native Claude agent in Claude Code, or the `claude` CLI from Codex, with the same prompt text and instructions not to edit files.

## Evidence rule (applies to implementers and reviewers)

A claim without evidence is not a finding and not a fix.

- Reviewer finding = location + reproduction (command, test, or request) + observed output + expected output. Unreproduced suspicions go under "Unverified" and do not block.
- Fix = failing-before output, the change, passing-after output, plus the full relevant suite.
- Frontend = screenshots of each changed screen state (desktop and mobile width), uploaded to the Linear issue as attachments and linked in the PR body. Never commit screenshots.

## Worktrees and branches

Every implementer and reviewer gets its own git worktree. Branch names use the Linear `gitBranchName` so the GitHub integration links the PR. Large work: base `project/<project-slug>`; small work: base `develop`.
