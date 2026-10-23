# Workgraph conventions

Every skill exposed under `skills/`, including `improve-codebase-architecture`, follows these rules. Upstream skills live verbatim under `${WORKGRAPH_ROOT}/vendor/` (pinned git submodules). When an upstream file and this file disagree, this file wins.

## Reading map

Every role reads **Host compatibility**, **Linear is the only document store**, **Handoff format** and **Evidence rule**. Then read only its own sections; skip the rest unless a step points there.

| Role | Also read |
|---|---|
| `wg` coordinator | everything |
| grill, spec | Sizing, Issue format |
| architect, plan | Sizing, Issue format, Labels, Risk |
| implementer | Issue format, Status flow, Labels, Verification runs, Worktrees |
| reviewer, lead judge | Labels, Risk, Cross-model reviewer roster, Verification runs |
| close verifier, auditor, judge | Status flow, PR review and merge, Verification runs, Work metrics |

## Host compatibility (Codex and Claude Code)

`WORKGRAPH_ROOT` is the installed plugin root, resolved from the selected skill's `SKILL.md` as described there. Read upstream files from that root, while running code and git commands in the target repository/worktree. If `vendor/` is missing, stop and initialize the clone's submodules (`git submodule update --init --recursive`); do not invent upstream instructions. These conventions and the stage's overrides take precedence over upstream host-specific instructions.

Invoke stages as `$wg` / `$wg-spec` in Codex or `/wg` / `/wg-spec` in Claude Code; the same files serve both hosts. A reference to another stage means read its `skills/<stage>/SKILL.md` under `WORKGRAPH_ROOT`.

- **Delegation:** `Agent`, `general-purpose`, `run_in_background`, and `SendMessage` in stage instructions describe Claude Code operations. In Codex, use the available native agent spawn, message, and wait tools for the equivalent bounded assignment. Create each worktree explicitly and pass its absolute path; Claude's `isolation: "worktree"` is not a Codex option. Use only capabilities exposed by the current host. If delegation is unavailable, run independent assignments sequentially through the required model's CLI, retaining separate worktrees and prompts.
- **Model identity:** a native subagent belongs to the current host's model family. Codex native agents are `codex`; Claude Code native agents are `claude`. Never label a native Codex agent as Claude. The default implementer uses the current host's family; record the actual author family for every issue.
- **Other family:** from Codex, run Claude assignments using an authenticated `claude` CLI in the assigned worktree with a prompt file, for example `(cd "<worktree>" && claude -p < "<tmp>/prompt.md" > "<tmp>/result.md")`. From Claude Code, use `codex exec` as below. Pass the full upstream prompt body and task context to either CLI; referring to a Claude agent name does not load it in Codex. Keep the CLI's normal permission controls, and pre-approve what the assignment must run instead of loosening the mode: pass the repo's focused test, typecheck, lint and build commands with `--allowedTools` (for example `--allowedTools "Read" "Grep" "Glob" "Bash(pnpm vitest:*)" "Bash(pnpm exec tsc:*)"`) and tell it to run one command per call, without `&&`, `;`, pipes, `cd` or variables, because a headless run cannot answer approval prompts.
- **CLI assignments:** before the first CLI assignment of a session, run a one-line smoke prompt with the exact flags (model, effort, sandbox) you will use, and fix a rejected flag once there rather than in every assignment. A CLI assignment is a leaf worker: its prompt says not to spawn subagents. A CLI run that ends without a result is rerun once on the same SHA, then reported.
- **Language:** write every user-facing message in the user's language for the whole run.
- **Required capabilities:** discover the connected Linear tools and map the operation names in these instructions to their exposed equivalents. Read stages need Linear access; PR stages also need authenticated `gh`. Cross-model stages require both authenticated model families and review/e2e stages need their specified test/browser tools. If a required capability is missing, report exactly what is unavailable and stop that stage; do not silently replace a cross-model panel with one family or claim checks passed.

## Linear is the only document store

Never write specs, plans, task lists, ADRs, design notes or review reports into the code repository (`docs/`, `tasks/`, `specs/`, `plan.md`, …). Upstream skills that say "save to a file" save to Linear instead:

| Artifact | Large work | Small work |
|---|---|---|
| Spec (what and why) | Linear **project** description | Linear **issue** description |
| Architecture (types, signatures, boundaries, rationale) | Linear **document** named `Architecture` attached to the project | `## Design` section of the issue |
| Decision (chosen option, rationale, rejected alternatives) | `## Decisions` in the relevant Linear project description or `Architecture` document | `## Decisions` in the relevant Linear issue |
| Task | Linear **issue** in the project | the same single issue |
| Prerequisite DAG | issue `blocks` / `blockedBy` relations | — |
| Test design | `## Test design` section of each issue | same |
| Implementation evidence | GitHub PR body (Linear links it automatically) | same |
| Review findings | GitHub PR review comments | same |
| Leftover work | new Linear issues in the same project | new issues |

Do not offer, create, or update ADR files, load upstream ADR templates, or introduce a `docs/adr/` workflow. Upstream instructions to record an ADR instead record the chosen option, rationale, and rejected alternatives in the Linear decision location above. Upstream ADR prerequisites and report callouts use the relevant Linear decisions and links instead. Do not require a repository ADR directory.

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

- `needs-human`: the pipeline stopped and waits for a person; the latest issue comment gives the question, the options with their consequences, a recommendation, and the evidence links. The person removes the label and reruns `wg <project>` (or `wg <ISSUE-ID>`) to resume; removing the label alone wakes nothing.
- `interface`: the issue lands architect-defined types, signatures or schemas that other issues build on. Its PR must pass AI review and merge into the project branch before any blocked issue starts; no separate human merge is required.

Plus the existing type labels (`Feature`, `Bug`, `Improvement`).

## Risk = Estimate = reviewer count

The issue **Estimate** is its risk, not its effort. `wg-plan` sets it on every issue.

- reviewer count `n = min(estimate, 5)`; no estimate → stop and set one.
- Raise the estimate for: money, auth/permissions, personal data, migrations, concurrency, public API/`interface` issues, anything irreversible.
- When `n ≥ 2`, a `wg-implement` pre-review by model `B` on the PR's exact head SHA, with no unresolved findings, fills one round-1 `B` slot (focus 2); spawn the remaining `n - 1`. Any commit after it voids the credit. With `n = 1` there is no credit: the pre-review is a generic pass without focus 1 or the evidence rule, so the round-1 reviewer always runs.

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
codex exec -s read-only -C "<worktree>" -o "<tmp>/review-<r>-<i>.md" - < "<tmp>/prompt-<r>-<i>.md"
```

Keep the configured sandbox and permission controls on every host. If a sandbox prevents a required reproduction, report the limitation rather than changing to unrestricted access. Reviewers must not edit repository files. Check `git -C "<worktree>" status --porcelain` afterwards; discard results from an unexpectedly dirty worktree.

Running a Claude reviewer: use a native Claude agent in Claude Code, or the `claude` CLI from Codex, with the same prompt text and instructions not to edit files.

A CLI reviewer cannot write files from a read-only sandbox: it prints its full findings as its final message, and `-o` (codex) or the stdout redirect (`claude -p`) saves them to the findings path. Only a native subagent writes the file itself.

## Evidence rule (applies to implementers and reviewers)

A claim without evidence is not a finding and not a fix.

- Reviewer finding = location + reproduction (command, test, or request) + observed output + expected output. Unreproduced suspicions go under "Unverified" and do not block.
- Fix = failing-before output, the change, passing-after output, plus the full relevant suite.
- Frontend = screenshots of each changed screen state (desktop and mobile width), uploaded to the Linear issue as attachments and linked in the PR body. Never commit screenshots.

## Handoff format

Every assignment from the coordinator and every report back uses these headings, so nothing is lost between contexts.

- **Assignment:** role and stage; issue / PR and its base or pinned SHA; worktree (the only place to edit); inputs as Linear links and temp paths; expected output and where it goes; stop conditions.
- **Report:** result (`done`, `blocked` or `needs-human`); the SHA it applies to; evidence as run records, reproductions and output paths; open items and what unblocks them; the Work metrics fields it knows; the next action it recommends.

Reports carry conclusions and paths, never file dumps or raw review text.

## Work metrics

Recorded per issue as one Linear comment headed `Metrics`, when its PR merges or it stops on `needs-human`: author model and effort, review rounds, Act-on / Consider / Dismissed counts, Unverified findings later confirmed, fix attempts per Act-on finding, `needs-human` stops and their reason, check-lane contention reruns, and wall time from `In Progress` to merge. A high Dismissed share means reviewer prompts need work; repeated rounds on one focus mean the implementer prompt or the Test design missed it.

## Verification runs

- A full-suite, build or migration result belongs to one commit SHA. Record each run as SHA, command, environment as seen by the process that ran the tests (runtime version, worker count), pass/fail counts and duration, in the PR body's Verification section.
- Later stages on the same SHA (verifier, reviewers, coordinator) cite that record instead of rerunning it. Rerun only a focused reproduction for a specific claim, or everything when the SHA changed.
- **Check lane:** one full suite, build, dependency install or local DB reset runs at a time on a machine; focused tests may run in parallel. Whoever runs the heavy job takes the lane itself with a machine-local lock: `mkdir "<os-tmp>/wg-check-lane"` succeeding means you hold it; write your role, issue, SHA and start time into `owner` inside it, and remove the directory when the job ends, including on failure. If it exists, run focused work meanwhile and retry; a lock older than 2 hours whose owner is no longer running is stale, so remove it and note that in your report. A timeout seen while another heavy job ran is recorded as contention and rerun alone before it counts as a failure.

## Worktrees and branches

Every implementer and reviewer gets its own git worktree. Branch names use the Linear `gitBranchName` so the GitHub integration links the PR. Large work: base `project/<project-slug>`; small work: base `develop`.
