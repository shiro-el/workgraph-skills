---
name: wg-spec
description: Turn the decisions settled in wg-grill into a clean spec in Linear, show it as an HTML review page in the user's language, and record the confirmed spec in Linear. It organizes; it does not reopen the design. Use for $wg-spec in Codex or /wg-spec in Claude Code or right after wg-grill.
---

# wg-spec

Resolve `WORKGRAPH_ROOT` by resolving symlinks on this installed `SKILL.md`, then taking `../..` from its containing skill directory (the directory containing `conventions.md` and `vendor/`), never from the target repository or current working directory. Paths below use that resolved root; it is not a host-provided environment variable.

Read `${WORKGRAPH_ROOT}/conventions.md` first.

**Purpose.** The design was argued out in `wg-grill`. This stage writes those settled decisions down as a tidy spec, anchored in the real code, and lets the user check the write-up. It is not a second interview. The input is grill's decision list in the conversation (on resume, the Linear draft). Without one, run `wg-grill` first.

**When to ask.** Ask the user only when the code contradicts a settled decision or makes it impossible, so the spec cannot be written as decided (for example, a field the decision relies on does not exist and adding it changes the data model or a contract). Ask in chat, one question per contradiction, with a recommended answer and what changes. Everything else is yours to fill in as a proposal: screen placement, copy, error and empty states, ordering, naming. Write it into the spec; the user can correct it on the review page. Zero questions is the normal case.

## 1. Anchor the decisions in the code (feature-dev phase 2)

Launch 2–3 explorer subagents in parallel (`Agent`, `general-purpose`). Each one's prompt is the body of `${WORKGRAPH_ROOT}/vendor/claude-code/plugins/feature-dev/agents/code-explorer.md` followed by the grill decision list and its target, one per agent:

- features most similar to this one, traced end to end;
- the data model, API and permission layers this feature will touch;
- UI patterns, test harness and e2e setup in the affected area.

Each returns 5–10 key files. Read those files yourself before writing. The findings fill in paths, reused functions and test setup; they do not create new decisions. Check each decision against them and apply **When to ask** to any contradiction before step 2.

## 2. Write the spec in Linear (spec-kit specify)

Follow the structure of `${WORKGRAPH_ROOT}/vendor/spec-kit/templates/spec-template.md` and the quality rules of `${WORKGRAPH_ROOT}/vendor/spec-kit/templates/commands/specify.md`. Ignore everything there about branches, scripts, `specs/` folders, feature numbers, checklist files and generating clarification questions. Use the user's language for the spec and review prose, including Korean; preserve code identifiers, paths and the required Linear section headings.

Every grill decision appears in the spec, as behaviour, an acceptance criterion or an out-of-scope line. Add nothing grill did not settle except the details **When to ask** leaves to you. Additions to the template:

- `## Integration with the existing system`: for each touched module, what changes, what stays, which existing function/table/endpoint is reused (by path), and the migration or rollout order.
- `## Decisions`: grill's decisions, dated, each with the rejected alternative, plus any decided in this stage.
- `## Open questions`: only what grill explicitly left open, and for large work the types, signatures and module boundaries left to `wg-architect`. Do not invent questions to fill it.
- `## Spec review` with `Pending` until the user has reviewed the page and the responses have been reflected in Linear.

Reuse the current Linear project or issue when resuming. Store the draft using the mapping in step 4, with status `Backlog` while review is pending.

## 3. Review page

Copy `${WORKGRAPH_ROOT}/vendor/html-effectiveness/16-implementation-plan.html` to `<temp>/spec.html` under an OS temp directory, never the target repository or plugin. Keep its license comment, `<style>` block and page layout unchanged, and replace only the content. Add one `<style>` block after the template's for what it lacks: `word-break: keep-all` on `.page` for Korean, `min-width: 0` on `.code-grid` children so code scrolls instead of widening the page, a plain table style for the decision and test tables, and the app-styled mock classes. The page is a read-through of the written spec, not a decision round and not a second spec store: generate it from the current Linear draft, and on resume reread Linear and regenerate rather than reuse a previous session's temp files.

- **Head.** The feature title; the Linear URL and the draft's revision time with its time zone where the template has its prompt box, so feedback can be matched to the draft; summary cells for size (small/large), Estimate, touched modules and migration (none or what kind).
- **Sections**, in this order, numbered like the template; drop a section that has nothing to show, and drop the template's milestones (`wg-plan` slices the work):
  1. Decisions — every grill decision with the chosen answer and the rejected alternative, as a table, then the details this stage filled in, marked as decided in `wg-spec`.
  2. Screens — for an existing screen, a screenshot of the running app embedded as a `data:` URI, then a mock of only the new or changed part, styled after the app's own components and copy. Long user-facing copy goes here in full so the user can correct it.
  3. Flow — an inline SVG of the request or state flow, only when the feature crosses more than one layer.
  4. Integration — per touched module, what changes, what stays and the reused function/table/endpoint by path, with the key code in the template's code blocks. Label proposed code as a sketch and show the existing code it changes beside it. For large work, leave unsettled types, signatures and module boundaries to `wg-architect`.
  5. Acceptance criteria and test design — the same rows as Linear, as tables.
  6. Out of scope and open questions.
- **Language.** Write the content in the user's language and set `<html lang>` to match (`ko` for Korean); keep UTF-8. Preserve quoted user text, code, identifiers and paths.
- **Evidence.** Before quoting code by path, read those lines and confirm they show what the text says. Every screenshot and mock must match the decision it illustrates.
- **Look, then hand over.** A browser pane may render `file://` pages outside the project as static snapshots, so serve the temp directory over `http://127.0.0.1` (for example `python -m http.server <port> --bind 127.0.0.1` in the background) and open the page there at 1280px and 375px wide (set the size explicitly; a narrow browser pane is not a desktop width). Check that nothing is clipped or overlapping, the SVG labels fit their shapes and the Korean text wraps cleanly; fix and recheck until it does. Stop the server afterwards. Give the user the HTML file and the Linear URL, ask them to reply in chat with corrections (or "확인" when it is right), then wait.
- **Reconcile feedback.** Apply each correction to the Linear spec, acceptance criteria and `## Decisions`. A correction describes the spec; it does not authorize implementing it at this stage. If the corrections change the proposal materially, regenerate the page from the updated Linear draft and show it again. Then continue to step 4.

## 4. Finalize in Linear

- Large: create or update the Linear project (`save_project`) with the spec as its description and a one-sentence summary. Status `Backlog`.
- Small: create the single issue (`save_issue`) with the team template, the spec as `## Background` / `## Scope`, plus `## Acceptance criteria`, `## Test design` and an Estimate per conventions. Status `Todo` once complete.

Update the draft created in step 2 rather than creating a duplicate. No `[NEEDS CLARIFICATION]` marker may block the next stage. Set `## Spec review` to `Complete` only after the user's review and feedback reconciliation. Store enough rationale in Linear for the next stage to proceed without the HTML file or the chat feedback.

Show the user the Linear URL (small: with the issue's Estimate, the reviewer count it sets, and its reason, for approval; then post the conventions `wg:estimate` marker on the issue) and stop. Next step: `wg-architect` (large) or `wg-implement` via `wg` (small).

**Override check.** After reading the upstream files and before acting on them, reread this file's purpose, **When to ask** and step 3. Where upstream and these overrides or `conventions.md` differ, the overrides win; skip the upstream parts they replace instead of reconciling them.
