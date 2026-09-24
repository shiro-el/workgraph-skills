---
name: plan-workgraph
description: Split a large software goal into reviewable issues with acceptance criteria, dependencies, and parallel-work conflicts. Use when planning a multi-PR implementation workflow.
---

# Plan a work graph

Turn the requested outcome into small changes that can each be implemented, reviewed, verified, and merged coherently. First inspect the relevant repository structure, existing tests, and the user's source specification. Preserve requirements and record unresolved assumptions. For a persistent multi-PR run, write one readable, structured work graph following [the graph format](references/workgraph-format.md); the full requirement text remains in the issues.

For each work item, record:

- Outcome and acceptance criteria, including important edge cases.
- Intended code areas and any shared API, schema, configuration, or behavior contract.
- A verification method that can show the item is complete.
- Prerequisite items that must land first.
- Likely interference with other work, including semantic conflicts even when files differ.

Keep **dependency** edges separate from **parallel conflict** edges. A dependency means another item must be implemented or merged first. A conflict means simultaneous work needs coordination or sequencing; shared files alone are a clue, not the full rule. Identify the ready items and a sensible merge order. Avoid splitting a coherent change so finely that its PR cannot be understood or tested.

Validate the graph with `scripts/validate_workgraph.py <path-to-workgraph.yaml>` before publishing or dispatching. Use `--dispatch-ready` before dispatch. The script requires PyYAML and checks structure, unique IDs, valid references, dependency cycles, and conflict pairs; it does not check remote GitHub state or semantic interference. Treat the graph as the source for scheduling topology. GitHub issue dependency links may mirror it for visibility; reconcile differences rather than silently choosing whichever view is convenient.

When the user has asked to create GitHub issues, create them and record their URLs. Use native issue dependency relationships when available. When the request is only to plan, return a reviewable draft without publishing. Link every published issue to its parent goal or tracking issue when one exists.

Return the work graph, parallel groups, risky seams, and any assumptions that could change the plan. Do not start implementation or spawn subagents in this skill.
