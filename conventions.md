# Workgraph conventions

Every `wg-*` skill follows these rules. Upstream skills live verbatim under `${CLAUDE_PLUGIN_ROOT}/vendor/` (pinned git submodules). When an upstream file and this file disagree, this file wins.

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

`Backlog` draft → `Todo` spec complete, may be dispatched → `In Progress` implementer working → `In Review` PR open → `Done` (set by the GitHub integration when a human merges). Agents never merge PRs.

## Labels

- `needs-human`: the pipeline stopped and waits for a person; the latest issue comment says why and what answer unblocks it. The person removes the label to resume.
- `interface`: the issue lands architect-defined types, signatures or schemas that other issues build on. Its PR needs a human merge before any blocked issue starts.

Plus the existing type labels (`Feature`, `Bug`, `Improvement`).

## Risk = Estimate = reviewer count

The issue **Estimate** is its risk, not its effort. `wg-plan` sets it on every issue.

- reviewer count `n = min(estimate, 5)`; no estimate → stop and set one.
- Raise the estimate for: money, auth/permissions, personal data, migrations, concurrency, public API/`interface` issues, anything irreversible.

## Cross-model reviewer roster

Models: `claude` (Agent tool, `general-purpose` subagent) and `codex` (`codex exec`). Let `A` be the model that wrote the code and `B` the other one. For review round `r` (1-based):

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

On Windows the `read-only` and `workspace-write` sandboxes cannot run commands. Use `-s danger-full-access` there, keep "do not edit files" in the prompt, and afterwards require `git -C "<worktree>" status --porcelain` to be empty. A dirty worktree means its output is discarded and the run repeated.

Running a claude reviewer: `Agent` with `subagent_type: general-purpose`, the same prompt text, and instructions not to edit files.

## Evidence rule (applies to implementers and reviewers)

A claim without evidence is not a finding and not a fix.

- Reviewer finding = location + reproduction (command, test, or request) + observed output + expected output. Unreproduced suspicions go under "Unverified" and do not block.
- Fix = failing-before output, the change, passing-after output, plus the full relevant suite.
- Frontend = screenshots of each changed screen state (desktop and mobile width), uploaded to the Linear issue as attachments and linked in the PR body. Never commit screenshots.

## Worktrees and branches

Every implementer and reviewer gets its own git worktree. Branch names use the Linear `gitBranchName` so the GitHub integration links the PR. Large work: base `project/<project-slug>`; small work: base `develop`.
