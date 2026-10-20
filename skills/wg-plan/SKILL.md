---
name: wg-plan
description: For large work only. Break the Linear project spec and Architecture document into small Linear issues with acceptance criteria, an exhaustive test design, a risk Estimate and a blocks/blockedBy DAG, then get an independent alternative-architecture critique and adjust. Use for /wg-plan after wg-architect.
---

# wg-plan

Read `${CLAUDE_PLUGIN_ROOT}/conventions.md`, then follow `${CLAUDE_PLUGIN_ROOT}/vendor/addyosmani-agent-skills/skills/planning-and-task-breakdown/SKILL.md` steps 1–5. Use `${CLAUDE_PLUGIN_ROOT}/vendor/spec-kit/templates/commands/tasks.md` for its dependency and parallelism rules. Overrides:

## Where things go

- Ignore `tasks/plan.md`, `tasks/todo.md` and spec-kit's `tasks.md`. Each task is a Linear issue in the project (`save_issue`, team template, label `Feature` / `Improvement` / `Bug`). Plan-level risks and open questions go into the project description's `## Open questions`.
- Each dependency is a Linear `blocks` relation. No cycles. The `interface` issue from the Architecture document comes first and blocks everything that uses its types.
- Every issue carries the conventions issue format: Background, Scope, Acceptance criteria, Test design, Out of scope. Add a `## Files likely touched` list and the slice of the Architecture document it implements, linked rather than copied.

## Slicing

Vertical slices. Size S or M; L is split. An issue with "and" in its title is split. Two issues that edit the same files are either sequenced with `blocks` or merged into one. Note the shared files in both issues.

## Test design is designed here, not during implementation

For each issue:

1. Write the Test design table yourself: every acceptance criterion gets one or more rows; every edge-case category in conventions is either a row or marked "n/a: reason".
2. Run one adversarial test-design reviewer on the model you are not (codex: `codex exec -s read-only`). Prompt: the issue, the Architecture slice, the relevant code paths; "list missing or wrong test cases only, each with Given/When/Then and why it matters". Fold in the valid ones.

## Risk Estimate

Set the Estimate on every issue per conventions (`n` reviewers). State the reason in one line under `## Background`.

## Alternative-architecture critique (automatic)

After the issue set is drafted, launch 2 critics in parallel, one claude (`Agent`, `general-purpose`) and one codex. Each critic's prompt is `${CLAUDE_PLUGIN_ROOT}/vendor/claude-code/plugins/feature-dev/agents/code-architect.md` (body) + the spec + the Architecture document + the issue list with its DAG. Task: "design your own alternative architecture and breakdown for this spec, then list concrete places where the given plan is worse: wrong boundaries, missing issues, wrong order, issues too big, hidden coupling, untestable criteria". Triage each point: adopt, reject with a reason, or put it to the user if it changes the Architecture. Apply the adopted changes to the issues and relations.

## Finish

Move ready issues (all text complete, Estimate set) from `Backlog` to `Todo`. Show the user the DAG (issue IDs and blocks edges) and the critique decisions. Next: `wg`, to dispatch.
