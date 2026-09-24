# Workgraph Skills

Ship large software changes through small, reviewable pull requests.

These skills split a goal into issues, coordinate parallel implementation, assign independent reviewers, merge verified work, and check the integrated result. The main agent chooses each subagent's model and reasoning effort. Every subagent gets a separate Git worktree.

The skills are composable. Use `plan-workgraph` to prepare the work, then `run-workgraph` to drive it to completion. Implementation, review, and final audit each have a focused skill.

## Installation

Install all five skills globally with the [Skills CLI](https://github.com/vercel-labs/skills). Choose the agent when prompted:

```sh
npx skills@latest add shiro-el/workgraph-skills --skill '*' -g
```

To preview the available skills before installing, run `npx skills@latest add shiro-el/workgraph-skills --list`.

## How it works

1. **Plan:** `plan-workgraph` turns the goal into issues with acceptance criteria, prerequisite links, and likely parallel-work conflicts.
2. **Execute:** `run-workgraph` dispatches ready issues to separate worktrees and selects models and effort based on each task's difficulty and risk.
3. **Review:** An independent agent checks each PR against its issue and the actual code diff. The implementation owner addresses confirmed findings.
4. **Integrate:** The coordinator merges verified PRs in dependency order, then audits the combined behavior and routes any integration fixes back through the loop.

The issue is the requirement source. A PR records the implementation and its verification evidence. The work graph records scheduling relationships; it does not replace either one.

## Skills

| Skill | Job |
| --- | --- |
| [`plan-workgraph`](skills/plan-workgraph/SKILL.md) | Break down the goal and identify dependencies and conflicts |
| [`run-workgraph`](skills/run-workgraph/SKILL.md) | Coordinate agents, reviews, merges, and completion evidence |
| [`implement-issue`](skills/implement-issue/SKILL.md) | Implement one issue and submit a scoped PR |
| [`review-issue-pr`](skills/review-issue-pr/SKILL.md) | Review one pinned PR revision independently |
| [`audit-integrated-work`](skills/audit-integrated-work/SKILL.md) | Verify the result across merged PRs |

The coordinator owns delegation and merge decisions. Implementation and review agents do not spawn further agents or approve their own work.

## Graph format and prerequisites

The optional persistent graph format is documented in [`workgraph-format.md`](skills/plan-workgraph/references/workgraph-format.md). Its validator requires Python and PyYAML (`python -m pip install PyYAML`). GitHub CLI access is needed when the workflow creates or reads issues and PRs.

## License

MIT. See [LICENSE](LICENSE).
