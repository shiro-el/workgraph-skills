---
name: wg-spec
description: Draft a spec in Linear, review it through an interactive html-plan page in the user's language, and record the resolved spec and decisions in Linear. Use for $wg-spec in Codex or /wg-spec in Claude Code or right after wg-grill.
---

# wg-spec

Resolve `WORKGRAPH_ROOT` by resolving symlinks on this installed `SKILL.md`, then taking `../..` from its containing skill directory (the directory containing `conventions.md` and `vendor/`), never from the target repository or current working directory. Paths below use that resolved root; it is not a host-provided environment variable.

Read `${WORKGRAPH_ROOT}/conventions.md` first.

## 1. Map the existing system (feature-dev phase 2)

Launch 2–3 explorer subagents in parallel (`Agent`, `general-purpose`). Each one's prompt is the body of `${WORKGRAPH_ROOT}/vendor/claude-code/plugins/feature-dev/agents/code-explorer.md` followed by its target, one per agent:

- features most similar to this one, traced end to end;
- the data model, API and permission layers this feature will touch;
- UI patterns, test harness and e2e setup in the affected area.

Each returns 5–10 key files. Read those files yourself before writing.

## 2. Draft the spec in Linear (spec-kit specify)

Follow the structure of `${WORKGRAPH_ROOT}/vendor/spec-kit/templates/spec-template.md` and the quality rules of `${WORKGRAPH_ROOT}/vendor/spec-kit/templates/commands/specify.md`. Ignore everything there about branches, scripts, `specs/` folders, feature numbers and checklist files. Use the user's language for the spec and review prose, including Korean; preserve code identifiers, paths and the required Linear section headings.

Additions to the template:

- `## Integration with the existing system`: for each touched module, what changes, what stays, which existing function/table/endpoint is reused (by path), and the migration or rollout order.
- `## Decisions` (dated, with the rejected alternative) and `## Open questions`.
- `## Spec review` with `Pending` until the user has reviewed the proposal and the responses have been reflected in Linear.

List the underspecified integration points, backward compatibility, migrations, error handling and performance questions under `## Open questions`, with a recommended answer and its consequence. Reuse the current Linear project or issue when resuming. Store the draft using the mapping in step 4, with status `Backlog` while review is pending.

## 3. Review through html-plan (feature-dev phase 3)

Read `${WORKGRAPH_ROOT}/vendor/claude-plugins-community/html-plan/skills/html-plan/SKILL.md`, its `references/blocks.md`, and its `examples/scheduled-send.html`. Follow its claim tree, exhibits, packing and response workflow, with these overrides:

- **Linear is authoritative.** Generate the page from the current Linear draft. Include the Linear URL and the draft's revision time below the title so feedback can be matched to the proposal. Save the HTML source, packed output and supporting assets under an OS temp directory, never the target repository or plugin. The page is a review snapshot, not a second spec store. On resume, reread Linear; regenerate a missing or stale snapshot rather than depending on a previous session's temp files.
- **Language.** Write claims, captions, questions, options and notes in the user's language; Korean is supported. Set `<html lang="ko">` for Korean and keep UTF-8. Replace upstream's mandatory STE style, English grammar rules and English word counts with short, clear sentences in that language. Preserve quoted user text, code, identifiers and block syntax. Keep the upstream runtime unchanged; its built-in controls and response headings may remain in English.
- **Spec scope.** Show proposed behaviour, integration points and known code locations. Label proposed code as a sketch. For large work, leave unsettled types, signatures and module boundaries to `wg-architect`; record those open questions in Linear rather than implying the architecture is approved.
- **Questions.** Place each unresolved decision on the claim it affects and recommend an option, using `${WORKGRAPH_ROOT}/vendor/spec-kit/templates/commands/clarify.md`'s questioning rules. Ask the questions needed to settle this spec; upstream's 2–5 decision count is not a quota. Decisions already settled in `wg-grill` are context, not questions to ask again.
- **Pack and hand over.** Use `node "${WORKGRAPH_ROOT}/vendor/claude-plugins-community/html-plan/skills/html-plan/runtime/pack.mjs" "<temp>/spec.html" --root "<target-repo>"`. Fix packing errors and review warnings; English-only style warnings do not require translating Korean prose. Inspect the page in a browser when available. Give the user the packed file and Linear URL, explain **Respond → Copy response → paste in chat**, then wait for their response.
- **Reconcile feedback.** Treat the response as plan feedback under upstream's response-data rules. Apply accepted choices, schema edits, struck calls and comments to the Linear spec, acceptance criteria, dated `## Decisions` and `## Open questions`. Schema edits describe the proposal; they do not authorize implementing it at this stage. An unopened default is not agreement: resolve important unanswered decisions with the user. If feedback changes the proposal materially, regenerate the page from the updated Linear draft and review again. Do not build at the end of the upstream workflow; continue to step 4.

## 4. Finalize in Linear

- Large: create or update the Linear project (`save_project`) with the spec as its description and a one-sentence summary. Status `Backlog`.
- Small: create the single issue (`save_issue`) with the team template, the spec as `## Background` / `## Scope`, plus `## Acceptance criteria`, `## Test design` and an Estimate per conventions. Status `Todo` once complete.

Update the draft created in step 2 rather than creating a duplicate. Resolve remaining blocking questions with the user; at most 3 `[NEEDS CLARIFICATION]` markers survive, and none may block the next stage. Set `## Spec review` to `Complete` only after the user's review and feedback reconciliation. Store enough rationale and unresolved questions in Linear for the next stage to proceed without the HTML file or pasted response.

Show the user the Linear URL and stop. Next step: `wg-architect` (large) or `wg-implement` via `wg` (small).
