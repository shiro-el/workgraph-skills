---
name: wg-review
description: Review one PR with a risk-sized, cross-model panel (claude and codex) that must back every finding with a reproduction, then loop fix → re-review until it passes. Hand intermediate PRs to the coordinator for merging and final PRs to a human. Use for $wg-review in Codex or /wg-review in Claude Code PR or when wg reaches a PR in In Review.
---

# wg-review

Resolve `WORKGRAPH_ROOT` by resolving symlinks on this installed `SKILL.md`, then taking `../..` from its containing skill directory (the directory containing `conventions.md` and `vendor/`), never from the target repository or current working directory. Paths below use that resolved root; it is not a host-provided environment variable.

Read `${WORKGRAPH_ROOT}/conventions.md` first. You are the lead reviewer and the loop driver. You never edit the PR's code and never merge.

## Each round

1. **Scope.** Pin the PR head SHA. Read the Linear issue (acceptance criteria, Test design, Estimate), the Architecture slice if any, the PR body and its evidence. State the intent in one paragraph, as in step 2 of `${WORKGRAPH_ROOT}/vendor/cursor-plugins/pstack/skills/interrogate/SKILL.md`.
2. **Roster.** `n = min(estimate, 5)`. Assign models and focuses for this round with the conventions roster rule, including the pre-review credit. The author model is the implementer's.
3. **Spawn** all reviewers at once, each in its own detached worktree at the pinned SHA (`git worktree add --detach <tmp>/rv-<r>-<i> <SHA>`). A fresh worktree has no dependencies: install them with the repo's frozen-lockfile command before spawning. If that is impossible, say so in the prompt and have the reviewer cite the implementer's run output for those checks, marked `not rerun`. Build every prompt from the template in `${WORKGRAPH_ROOT}/vendor/cursor-plugins/pstack/skills/interrogate/references/reviewer-prompt.md`, filled with:
   - the intent, the diff (`gh pr diff`), the issue text, the PR evidence;
   - `references/rubric.md` and `references/code-quality-review.md` from the same interrogate folder;
   - the reviewer's assigned focus from conventions;
   - the high-signal filter and false-positive list from `${WORKGRAPH_ROOT}/vendor/claude-code/plugins/code-review/commands/code-review.md` steps 4 and "Use this list…" (only flag what you can show; no pre-existing issues, no linter-level nits);
   - the evidence rule: "each finding = file:line, reproduction you actually ran, observed vs expected output. You may run tests and the app inside your worktree. Cite the recorded full-suite runs for this SHA instead of rerunning them; run focused reproductions. Unreproduced suspicions go under `Unverified`."
   - for round ≥ 2: the previous round's findings and the implementer's replies; "check each claimed fix by rerunning its reproduction, then review the new diff". Give the delta diff (`git diff <previous SHA>..<SHA>`) in place of the full PR diff, plus the PR's changed-file list; the reviewer reads the rest from its worktree (`git diff <base>...HEAD`).
4. **Synthesize and judge** per interrogate steps 4–5 and `references/lead-judgment.md`: merge duplicates, note which models raised each, bucket into Act on / Consider / Noted / Dismissed. A finding without a reproduction cannot be `Act on`. If you doubt one, validate it with one extra subagent on the other model, per code-review step 5.
5. **Post.** One `gh pr review` per round: `--request-changes` with the Act-on findings as inline comments (each with its reproduction), or `--comment` when nothing is Act on. Put the nonblocking Consider items in the review body; carry their links into the final PR for the human reviewer. GitHub refuses `--request-changes` on a PR opened by the same account; then post `--comment` whose body starts with `**Changes requested (round <r>)**` and carries the same findings.

## Loop

- Act-on findings → send them to the implementer (`wg-implement` "During review"). When it pushes, start round r+1 with the new head SHA. The roster flips.
- Round passes when it yields zero Act-on findings and every earlier Act-on item has rerun evidence that it is fixed. For an intermediate PR to `project/<slug>`, comment "Review passed at <SHA>: ready for coordinator merge" and report the PR URL, base branch, reviewed SHA and evidence to `wg`; no human review is required for this PR. For a final PR to `develop`, comment "Review passed at <SHA>: ready for final human review and merge" and report it to the user. Leave the issue `In Review` until the merge integration moves it to `Done`. When invoked directly on an intermediate PR, hand off to `wg` for the merge rather than asking the user to merge.
- After a `needs-human` stop that ends in a redesign, restart at round 1: the roster and focus rotation reset and the redesigned diff counts as new code. Earlier Act-on findings carry over only as reproductions to rerun.
- Stop and add `needs-human` (with a comment saying why) when the same finding survives 2 fix attempts, reviewers and implementer disagree with evidence on both sides, or a fix needs an `interface` change.
