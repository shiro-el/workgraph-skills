---
name: wg-architect
description: For large work only. Decide types, function signatures and module boundaries before any code, by running independent claude and codex design candidates and synthesizing them. Stores the result as the Linear project's Architecture document. Use for /wg-architect after wg-spec.
---

# wg-architect

Read `${CLAUDE_PLUGIN_ROOT}/conventions.md`, then follow `${CLAUDE_PLUGIN_ROOT}/vendor/cursor-plugins/pstack/skills/architect/SKILL.md` phases A–C. Its Phase B runs `${CLAUDE_PLUGIN_ROOT}/vendor/cursor-plugins/pstack/skills/arena/SKILL.md`. Overrides:

## Inputs

The Linear project description (the spec) and the explorer findings from `wg-spec`. Phase A grounding: if the exploration is missing or stale, rerun it with the feature-dev `code-explorer` prompt as in `wg-spec` step 1, instead of the pstack `how` / `why` skills.

## Runners (replaces `pstack-models.mdc`)

- At least 4 candidates: 2 on claude (`Agent`, `general-purpose`, `run_in_background: true`) and 2 on codex (`codex exec -s read-only -C <worktree> -o <tmp>/candidate-<n>.md`). Give each pair a different whole-shape direction, e.g. "smallest change, maximum reuse" vs "deepest module, smallest public surface". These directions come from feature-dev's architect phase.
- Every runner's prompt = `${CLAUDE_PLUGIN_ROOT}/vendor/cursor-plugins/pstack/skills/architect/references/runner-prompt.md` + `${CLAUDE_PLUGIN_ROOT}/vendor/claude-code/plugins/feature-dev/agents/code-architect.md` (body) + the spec + the grounding + its direction + its output path. Runners write only to their temp output path, never to the repo.
- Each runner gets its own detached worktree or temp dir.
- Cross-judge: run it on the model family that is not yours (you are claude, so codex). It gets the rubric and the candidates by label.
- Screen every candidate against `${CLAUDE_PLUGIN_ROOT}/vendor/cursor-plugins/pstack/skills/architect/references/design-red-flags.md`.

## Checkpoint is on by default

Phase C asks for a human checkpoint. Present the synthesized design (usage sketch, types, signatures, module map, boundaries, synthesis decision, rejected candidates) and wait for the user's approval. Pushback means re-ground and rerun Phase B.

## Output

- Linear document titled `Architecture` attached to the project (`save_document`), shaped by `${CLAUDE_PLUGIN_ROOT}/vendor/cursor-plugins/pstack/skills/architect/references/rationale-template.md`. Include the full type and signature sketch in code blocks. Nothing goes into the repo.
- Note in the document which parts become the `interface` issue. `wg-plan` creates that issue: it lands the types, signatures and `not implemented` stubs as its own PR.

Phases D–E (implement against the sketch, scrap when wrong) belong to `wg-implement`.
