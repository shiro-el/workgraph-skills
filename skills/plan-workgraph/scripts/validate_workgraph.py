#!/usr/bin/env python3
"""Validate the static scheduling topology in a workgraph YAML file."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
    from yaml.tokens import AliasToken, AnchorToken, TagToken
except ImportError:
    print("PyYAML is required: install it with `python -m pip install PyYAML`.", file=sys.stderr)
    raise SystemExit(2)


TASK_ID = re.compile(r"^[a-z][a-z0-9-]*$")
ISSUE_REF = re.compile(r"^[^/\s]+/[^/#\s]+#[1-9][0-9]*$")
ROOT_KEYS = {"schema_version", "goal_issue", "tasks", "conflicts"}
TASK_KEYS = {"id", "issue", "spec", "depends_on", "expected_paths", "contracts"}
CONFLICT_KEYS = {"tasks", "reason", "policy"}


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str):
            raise ValueError("mapping keys must be strings")
        if key in result:
            raise ValueError(f"duplicate mapping key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
)


def read_graph(path: Path) -> object:
    source = path.read_text(encoding="utf-8-sig")
    for token in yaml.scan(source):
        if isinstance(token, (AliasToken, AnchorToken, TagToken)):
            raise ValueError("YAML aliases, anchors, and explicit tags are not allowed")
    return yaml.load(source, Loader=UniqueKeyLoader)


def text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: object) -> bool:
    return isinstance(value, list) and all(text(item) for item in value)


def validate(graph: object, dispatch_ready: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(graph, dict):
        return ["root must be a mapping"]

    unknown = set(graph) - ROOT_KEYS
    if unknown:
        errors.append(f"unknown root keys: {', '.join(sorted(unknown))}")
    if type(graph.get("schema_version")) is not int or graph["schema_version"] != 1:
        errors.append("schema_version must be the integer 1")
    if "goal_issue" in graph and not (
        text(graph["goal_issue"]) and ISSUE_REF.fullmatch(graph["goal_issue"])
    ):
        errors.append("goal_issue must be an owner/repo#number reference")

    tasks = graph.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return errors + ["tasks must be a non-empty list"]

    by_id: dict[str, dict] = {}
    for index, task in enumerate(tasks):
        label = f"tasks[{index}]"
        if not isinstance(task, dict):
            errors.append(f"{label} must be a mapping")
            continue
        unknown = set(task) - TASK_KEYS
        if unknown:
            errors.append(f"{label} has unknown keys: {', '.join(sorted(unknown))}")
        task_id = task.get("id")
        if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
            errors.append(f"{label}.id must be a lowercase hyphenated ID")
            continue
        if task_id in by_id:
            errors.append(f"duplicate task ID: {task_id}")
        else:
            by_id[task_id] = task
        if "issue" in task and not (
            text(task["issue"]) and ISSUE_REF.fullmatch(task["issue"])
        ):
            errors.append(f"{task_id}.issue must be an owner/repo#number reference")
        if "spec" in task and not text(task["spec"]):
            errors.append(f"{task_id}.spec must be a non-empty string")
        if dispatch_ready and not ("issue" in task or "spec" in task):
            errors.append(f"{task_id} needs an issue or spec before dispatch")
        for field in ("depends_on", "expected_paths", "contracts"):
            if field == "depends_on" or field in task:
                if not string_list(task.get(field)):
                    errors.append(f"{task_id}.{field} must be a list of strings")

    edges: dict[str, list[str]] = {}
    for task_id, task in by_id.items():
        deps = task.get("depends_on")
        if not string_list(deps):
            continue
        if len(deps) != len(set(deps)):
            errors.append(f"{task_id}.depends_on has duplicate references")
        edges[task_id] = deps
        for dep in deps:
            if dep not in by_id:
                errors.append(f"{task_id} depends on unknown task {dep}")
            elif dep == task_id:
                errors.append(f"{task_id} depends on itself")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, path: list[str]) -> None:
        if task_id in visiting:
            errors.append("dependency cycle: " + " -> ".join(path + [task_id]))
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dep in edges.get(task_id, []):
            if dep in by_id:
                visit(dep, path + [task_id])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in by_id:
        visit(task_id, [])

    conflicts = graph.get("conflicts", [])
    if not isinstance(conflicts, list):
        return errors + ["conflicts must be a list"]
    seen_pairs: set[frozenset[str]] = set()
    for index, conflict in enumerate(conflicts):
        label = f"conflicts[{index}]"
        if not isinstance(conflict, dict):
            errors.append(f"{label} must be a mapping")
            continue
        unknown = set(conflict) - CONFLICT_KEYS
        if unknown:
            errors.append(f"{label} has unknown keys: {', '.join(sorted(unknown))}")
        pair = conflict.get("tasks")
        if not string_list(pair) or len(pair) != 2:
            errors.append(f"{label}.tasks must contain exactly two task IDs")
        else:
            key = frozenset(pair)
            if len(key) != 2:
                errors.append(f"{label} has a self-conflict")
            if key in seen_pairs:
                errors.append(f"{label} duplicates a conflict pair")
            seen_pairs.add(key)
            for task_id in pair:
                if task_id not in by_id:
                    errors.append(f"{label} references unknown task {task_id}")
        if not text(conflict.get("reason")):
            errors.append(f"{label}.reason must be a non-empty string")
        if conflict.get("policy") not in ("serialize", "coordinate"):
            errors.append(f"{label}.policy must be serialize or coordinate")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, help="path to workgraph.yaml")
    parser.add_argument(
        "--dispatch-ready", action="store_true", help="require an issue or spec for each task"
    )
    args = parser.parse_args()
    try:
        graph = read_graph(args.graph)
        errors = validate(graph, args.dispatch_ready)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Invalid work graph: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Valid work graph: {len(graph['tasks'])} tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
