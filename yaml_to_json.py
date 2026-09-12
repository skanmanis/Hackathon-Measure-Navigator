"""Compile and validate an English-readable measure decision tree."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent


def validate(tree: dict, check_catalog: dict) -> None:
    required = {"tree_id", "measure_id", "start", "nodes", "conclusions"}
    missing = required - tree.keys()
    if missing:
        raise ValueError(f"Decision tree missing keys: {sorted(missing)}")
    nodes, conclusions = tree["nodes"], tree["conclusions"]
    if tree["start"] not in nodes:
        raise ValueError(f"start references unknown node: {tree['start']}")
    check_ids = {item["check_id"] for item in check_catalog["checks"]}
    targets = set(nodes) | set(conclusions)
    for node_id, node in nodes.items():
        if node.get("type") == "check":
            if node.get("check_id") not in check_ids:
                raise ValueError(f"{node_id} references unknown check_id: {node.get('check_id')}")
            for status in ("MET", "NOT_MET", "OPEN_CONDITION"):
                if status not in node.get("on", {}):
                    raise ValueError(f"{node_id} has no {status} route")
            links = node["on"].values()
        elif node.get("type") == "router":
            if not node.get("options"):
                raise ValueError(f"{node_id} router has no options")
            links = [item.get("goto") for item in node["options"]]
        else:
            raise ValueError(f"{node_id} has unsupported type: {node.get('type')}")
        for target in links:
            if target not in targets:
                raise ValueError(f"{node_id} references unknown target: {target}")


def compile_tree(source: Path, output: Path, catalog_path: Path) -> dict:
    tree = yaml.safe_load(source.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    validate(tree, catalog)
    compiled = {
        "_meta": {
            "generated_from": source.name,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "warning": "GENERATED FILE - do not hand-edit. Edit the source YAML and run yaml_to_json.py.",
        },
        **tree,
    }
    output.write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8")
    return compiled


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "decision_tree.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "decision_tree.generated.json")
    parser.add_argument("--catalog", type=Path, default=ROOT / "check_catalog.json")
    args = parser.parse_args()
    result = compile_tree(args.source, args.output, args.catalog)
    print(f"Validated {len(result['nodes'])} nodes and wrote {args.output}")
