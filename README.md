# Workgraph

A Claude Code plugin for one personal pipeline: Linear holds every spec, plan and decision; the repo holds only code.

```
wg-grill → wg-spec → [large: wg-architect → wg-plan] → wg-implement (TDD, per issue, own worktree)
        → wg-review (risk-sized claude + codex panel, evidence-backed, loops) → human merge → [large: wg-close]
```

`/wg` is the entry point and coordinator. It reads the state from Linear, so any session can resume.

## Built from upstream, not rewritten

The skills here are thin overlays. The upstream skills are pinned git submodules under `vendor/`; GitHub stores only the commit pointers. Each overlay says "follow upstream X, except …".

| Stage | Upstream |
|---|---|
| grill | mattpocock/skills `grilling` |
| spec | anthropics/claude-code `feature-dev` (explorer, phases 2–3) + github/spec-kit `specify`, `clarify` |
| architect | cursor/plugins pstack `architect` + `arena` + feature-dev `code-architect` |
| plan | addyosmani/agent-skills `planning-and-task-breakdown` + spec-kit `tasks` + feature-dev `code-architect` critique |
| implement | addyosmani `test-driven-development`, `browser-testing-with-devtools` + feature-dev `code-reviewer` |
| review | pstack `interrogate` + claude-code `code-review` signal filter |
| close | spec-kit `analyze` |

Shared rules (Linear mapping, statuses, labels, Estimate → reviewer count, cross-model roster, evidence rule) are in [`conventions.md`](conventions.md).

## Install (local, so the submodules resolve)

```sh
git clone --recurse-submodules https://github.com/shiro-el/workgraph-skills.git
claude plugin marketplace add ./workgraph-skills
claude plugin install workgraph@workgraph
```

A marketplace added from a local path loads the plugin in place, so `vendor/` is present. Requirements: Linear MCP, `gh`, `codex` CLI.

## Update an upstream

```sh
git -C vendor/<name> fetch --depth 1 origin main && git -C vendor/<name> checkout FETCH_HEAD
git diff --submodule=diff vendor/<name>   # read what changed, then adjust the overlay
```

## License

MIT for this repo's own files. Each submodule keeps its own license; `vendor/claude-code` is © Anthropic and is referenced, not redistributed.
