# Work graph format

For a persistent repository workflow, use a single `docs/workgraph.yaml` file as the authoritative **scheduling topology**. Keep full requirements and acceptance criteria in the linked issues, and live PR/check/merge status in GitHub or a separate run ledger. Do not duplicate those mutable fields in the graph.

Use a small YAML subset: strings, lists, maps, and integers only. Avoid anchors, aliases, custom tags, implicit dates, and executable content. Example:

```yaml
schema_version: 1
goal_issue: "acme/shop#100"
tasks:
  - id: api-contract
    issue: "acme/shop#101"
    depends_on: []
    expected_paths: ["src/api/**"]
    contracts: ["Order response v2"]
  - id: checkout-ui
    issue: "acme/shop#102"
    depends_on: [api-contract]
    expected_paths: ["src/ui/checkout/**"]
    contracts: ["Order response v2"]
  - id: admin-ui
    issue: "acme/shop#103"
    depends_on: [api-contract]
    expected_paths: ["src/ui/admin/**"]
    contracts: ["Shared theme tokens"]
conflicts:
  - tasks: [checkout-ui, admin-ui]
    reason: "Both may revise shared theme tokens"
    policy: coordinate
```

`depends_on` is a directed prerequisite edge. `conflicts` is an undirected concurrency constraint or coordination warning; `policy` is `serialize` or `coordinate`. `expected_paths` predicts likely edits and is not an access-control boundary. `contracts` names shared interfaces or behavior that need agreement. An issue reference may be omitted in a draft before publication, but every dispatched task must resolve to an issue or equivalent spec.

Before using the graph for scheduling, run `scripts/validate_workgraph.py <path-to-workgraph.yaml> --dispatch-ready` from the `plan-workgraph` skill directory. It requires PyYAML. The validator checks unique task IDs, references, self edges, dependency cycles, duplicate conflict pairs, and conflict reason/policy. Check current issue state and prerequisite completion separately. Mirror `depends_on` into GitHub issue dependencies when available; if the two views differ, stop scheduling the affected item and reconcile them.

Keep worktree ownership and agent progress in the run ledger. They change during execution and do not belong in this planning graph.
