---
name: improve-codebase-architecture
description: Scan an existing codebase for architecture deepening opportunities, present a visual HTML report, then explore the user's chosen refactor. Use for $improve-codebase-architecture in Codex or /improve-codebase-architecture in Claude Code.
---

# Improve Codebase Architecture

Resolve `WORKGRAPH_ROOT` by resolving symlinks on this installed `SKILL.md`, then taking `../..` from its containing skill directory. Resolve the upstream paths below from that root, while exploring the user's target repository.

Follow `${WORKGRAPH_ROOT}/vendor/mattpocock-skills/skills/engineering/improve-codebase-architecture/SKILL.md` with the overrides below. Read `${WORKGRAPH_ROOT}/conventions.md` first; its document-storage and host compatibility rules also apply to this skill and its upstream dependencies. These overrides take precedence over upstream instructions.

- Read `${WORKGRAPH_ROOT}/vendor/mattpocock-skills/skills/engineering/codebase-design/SKILL.md` for the shared design vocabulary before exploring. Its relative references resolve from that upstream directory.
- When upstream calls the Skill tool for `grilling`, read and follow `${WORKGRAPH_ROOT}/vendor/mattpocock-skills/skills/productivity/grilling/SKILL.md`. For `domain-modeling`, use only the terminology clarification and scenario checks in `${WORKGRAPH_ROOT}/vendor/mattpocock-skills/skills/engineering/domain-modeling/SKILL.md`; its file-writing and ADR instructions are replaced by the decision-storage rules below. Do not load `ADR-FORMAT.md`. These dependencies do not need separate installation or a Claude-specific Skill tool.
- Use the host's available native agent tools for upstream's exploration and alternative-design assignments. If delegation is unavailable, perform the assignments sequentially yourself and state that limitation.
- Read `${WORKGRAPH_ROOT}/vendor/mattpocock-skills/skills/engineering/improve-codebase-architecture/HTML-REPORT.md` before generating the report. Keep the report in the OS temp directory, use the user's language, and provide its absolute path as a clickable link. Use an available browser/open command to display it; if unavailable, give the link without claiming it opened.
- Present the candidates and wait for the user's selection before designing an interface or making refactoring changes. This review does not automatically start the `wg` pipeline. If the user asks to move the chosen work into implementation, follow `skills/wg/SKILL.md` from `WORKGRAPH_ROOT`.

## Decisions and report context

- Replace upstream's `docs/adr/` exploration and prerequisites with the relevant Linear project/issue decisions and `Architecture` document. Use existing code and terminology for grounding; do not require repository ADR files.
- Do not propose, create, or update ADRs, even when a candidate is rejected for a lasting reason. Record the decision, rationale, and rejected alternatives in `## Decisions` of the relevant Linear project/issue or `Architecture` document, per conventions. Resolved domain terminology also goes into that Linear context; do not create or update `GLOSSARY.md` through this workflow.
- Replace the report scaffold's ADR callout with a callout for conflicts with a recorded Linear decision, linked to its source. Explain why revisiting it may be warranted; the user decides whether it changes.
- Exploration and the temporary HTML report may proceed without Linear. Before persisting decisions, identify the relevant Linear project/issue from the user's context. If none can be identified, ask for that target. If Linear is unavailable, keep the result in the conversation and report that persistence remains pending; never fall back to repository documentation or claim it was saved.

**Override check.** After reading the upstream files and before acting on them, reread this file's overrides. Where upstream and these overrides or `conventions.md` differ, the overrides win; skip the upstream parts they replace instead of reconciling them.
