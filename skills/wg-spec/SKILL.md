---
name: wg-spec
description: Turn settled decisions into a spec that says how the feature attaches to the existing system, and store it in Linear (project description for large work, issue description for small work). Use for /wg-spec or right after wg-grill.
---

# wg-spec

Read `${CLAUDE_PLUGIN_ROOT}/conventions.md` first.

## 1. Map the existing system (feature-dev phase 2)

Launch 2–3 explorer subagents in parallel (`Agent`, `general-purpose`). Each one's prompt is the body of `${CLAUDE_PLUGIN_ROOT}/vendor/claude-code/plugins/feature-dev/agents/code-explorer.md` followed by its target, one per agent:

- features most similar to this one, traced end to end;
- the data model, API and permission layers this feature will touch;
- UI patterns, test harness and e2e setup in the affected area.

Each returns 5–10 key files. Read those files yourself before writing.

## 2. Clarify (feature-dev phase 3)

List every underspecified point the exploration surfaced (integration points, backward compatibility, migrations, error handling, performance). Ask them as one numbered round with a recommended answer each, in the `grilling` format. Wait for answers.

## 3. Write the spec (spec-kit specify)

Follow the structure of `${CLAUDE_PLUGIN_ROOT}/vendor/spec-kit/templates/spec-template.md` and the quality rules of `${CLAUDE_PLUGIN_ROOT}/vendor/spec-kit/templates/commands/specify.md`. Ignore everything there about branches, scripts, `specs/` folders, feature numbers and checklist files.

Additions to the template:

- `## Integration with the existing system`: for each touched module, what changes, what stays, which existing function/table/endpoint is reused (by path), and the migration or rollout order.
- `## Decisions` (dated, with the rejected alternative) and `## Open questions`.
- At most 3 `[NEEDS CLARIFICATION]` markers survive; resolve the rest with the user via `${CLAUDE_PLUGIN_ROOT}/vendor/spec-kit/templates/commands/clarify.md`'s questioning rules.

## 4. Store it in Linear

- Large: create or update the Linear project (`save_project`) with the spec as its description and a one-sentence summary. Status `Backlog`.
- Small: create the single issue (`save_issue`) with the team template, the spec as `## Background` / `## Scope`, plus `## Acceptance criteria`, `## Test design` and an Estimate per conventions. Status `Todo` once complete.

Show the user the Linear URL and stop. Next step: `wg-architect` (large) or `wg-implement` via `wg` (small).
