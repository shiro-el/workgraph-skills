# Workgraph

A Codex and Claude Code plugin for one personal pipeline: Linear holds every spec, plan and decision; the repo holds only code.

```
wg-grill → wg-spec → [large: wg-architect → wg-plan] → wg-implement (TDD, per issue, own worktree)
        → wg-review (risk-sized claude + codex panel, evidence-backed, loops) → human merge → [large: wg-close]
```

`$wg` in Codex (`/wg` in Claude Code) is the entry point and coordinator. It reads the state from Linear, so any session can resume.

## Built from upstream, not rewritten

The skills here are thin overlays. The upstream skills are pinned git submodules under `vendor/`; GitHub stores only the commit pointers. Each overlay says "follow upstream X, except …".

| Stage | Upstream |
|---|---|
| grill | mattpocock/skills `grilling` |
| spec | anthropics/claude-code `feature-dev` (explorer, phases 2–3) + github/spec-kit `specify`, `clarify` + anthropics/claude-plugins-community `html-plan` |
| architect | cursor/plugins pstack `architect` + `arena` + feature-dev `code-architect` |
| plan | addyosmani/agent-skills `planning-and-task-breakdown` + spec-kit `tasks` + feature-dev `code-architect` critique |
| implement | addyosmani `test-driven-development`, `browser-testing-with-devtools` + feature-dev `code-reviewer` |
| review | pstack `interrogate` + claude-code `code-review` signal filter |
| close | spec-kit `analyze` |

Shared rules (Linear mapping, statuses, labels, Estimate → reviewer count, cross-model roster, evidence rule) are in [`conventions.md`](conventions.md).

`wg-spec` drafts the spec in Linear and presents an interactive html-plan page for review. Use the user's language, including Korean, for the spec, questions and captions. Paste the page's **Respond → Copy response** output into chat; the agent reconciles it into Linear before advancing. HTML files are temporary review snapshots outside the repository. Linear keeps the spec, decisions and open questions, so another session can resume a pending review without the original page.

## Install in Codex

### Direct skills (works with plugins disabled)

From a clone with initialized submodules:

```sh
python3 scripts/install-codex.py
```

This links all eight skills into `$CODEX_HOME/skills` (default `~/.codex/skills`), preserving their access to the full clone. It refuses to replace conflicting skills and is safe to rerun. Run it in the same environment as Codex; keep the clone at its installed location. Restart Codex, then use `$wg` in a chat for your target repository. To uninstall, remove only the eight `wg` / `wg-*` symlinks created by the installer.

### Plugin installation

Choose either direct skills or the plugin to avoid duplicate skill entries. Plugin installation requires `features.plugins = true` in the Codex environment.

Use a local clone with initialized submodules: the skills depend on both `conventions.md` and the pinned upstream files under `vendor/`. Installing just the individual skill folders loses those dependencies.

```sh
git clone --recurse-submodules https://github.com/shiro-el/workgraph-skills.git
cd workgraph-skills
# For an existing clone:
git submodule update --init --recursive
codex plugin marketplace add .
codex plugin add workgraph@workgraph
```

Restart Codex after installation. In a chat for the repository you want to work on, invoke `$wg <idea | ISSUE-ID | project>` or a specific stage such as `$wg-review <PR>`. The plugin uses the same eight skills in both hosts. The Codex package and local marketplace follow the [official plugin format](https://developers.openai.com/plugins/build/plugins).

Requirements: connected Linear tools, authenticated `gh`, and both authenticated `claude` and `codex` CLIs for cross-model stages. Codex uses native Codex agents and calls the Claude CLI for Claude assignments; Claude Code does the reverse. Stages report missing capabilities instead of silently skipping required reviewers or verification. Browser verification also requires browser tools in the runner's environment.

`wg-spec` also requires Node.js to pack the HTML review page; html-plan has no other runtime dependencies. Its built-in controls and generated response headings may remain in English while the review content is Korean.

The repo marketplace is `.agents/plugins/marketplace.json`; `.codex-plugin/plugin.json` declares the shared `skills/` directory. Keep the full clone in place so the upstream files remain available. See [`conventions.md`](conventions.md) for host-specific execution rules.

## Install in Claude Code (local, so the submodules resolve)

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
