"""Validate and retrieve a bounded neighborhood from a repository ontology map."""

import argparse
import json
import sys
from pathlib import Path


def load_graph(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate(graph):
    errors = []
    if graph.get("version") != 1:
        errors.append("version must be 1")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, dict):
        return errors + ["nodes must be an object"]
    if not isinstance(edges, list):
        return errors + ["edges must be an array"]
    for name, node in nodes.items():
        where = f"nodes.{name}"
        if not isinstance(node, dict):
            errors.append(f"{where} must be an object")
            continue
        if not name or name.strip() != name:
            errors.append(f"{where} has an invalid name")
        if node.get("kind") not in {"entity", "value_object", "process", "concept"}:
            errors.append(f"{where}.kind is invalid")
        if not isinstance(node.get("description"), str) or not node["description"].strip():
            errors.append(f"{where}.description is required")
        if not isinstance(node.get("sources"), list) or not node["sources"] or not all(isinstance(source, str) and source.strip() for source in node["sources"]):
            errors.append(f"{where}.sources must be nonempty paths")
        if node.get("review") not in {"proposed", "confirmed"}:
            errors.append(f"{where}.review is invalid")
        if "table" in node or "fields" in node:
            errors.append(f"{where} contains storage details; use implementation bindings")
        if "rules" in node and not isinstance(node["rules"], list):
            errors.append(f"{where}.rules must be an array")
        attributes = node.get("attributes")
        if not isinstance(attributes, dict):
            errors.append(f"{where}.attributes must be an object")
            continue
        for attribute_name, attribute in attributes.items():
            if not isinstance(attribute, dict) or not isinstance(attribute.get("description"), str) or not attribute["description"].strip():
                errors.append(f"{where}.attributes.{attribute_name}.description is required")
    seen = set()
    for index, edge in enumerate(edges):
        where = f"edges[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{where} must be an object")
            continue
        for endpoint in ("from", "to"):
            if edge.get(endpoint) not in nodes:
                errors.append(f"{where}.{endpoint} must name a node")
        if not isinstance(edge.get("type"), str) or not edge["type"].strip():
            errors.append(f"{where}.type is required")
        if not isinstance(edge.get("description"), str) or not edge["description"].strip():
            errors.append(f"{where}.description is required")
        if not isinstance(edge.get("sources"), list) or not edge["sources"] or not all(isinstance(source, str) and source.strip() for source in edge["sources"]):
            errors.append(f"{where}.sources must be nonempty paths")
        if edge.get("review") not in {"proposed", "confirmed"}:
            errors.append(f"{where}.review is invalid")
        if "join" in edge:
            errors.append(f"{where}.join is an implementation detail; use implementation bindings")
        if "rules" in edge and not isinstance(edge["rules"], list):
            errors.append(f"{where}.rules must be an array")
        signature = (edge.get("from"), edge.get("type"), edge.get("to"))
        if signature in seen:
            errors.append(f"{where} duplicates an edge")
        seen.add(signature)
    return errors


def validate_bindings(bindings, graph):
    errors = []
    if bindings.get("version") != 1:
        errors.append("bindings version must be 1")
    concepts = bindings.get("concepts")
    relationships = bindings.get("relationships")
    if not isinstance(concepts, dict) or not isinstance(relationships, list):
        return errors + ["bindings require concepts object and relationships array"]
    for concept, models in concepts.items():
        if concept not in graph["nodes"]:
            errors.append(f"bindings concept is not a graph node: {concept}")
        if not isinstance(models, list) or not models:
            errors.append(f"bindings.{concept} must be a nonempty array")
            continue
        for model in models:
            if not isinstance(model, dict) or not model.get("table") or not model.get("sources"):
                errors.append(f"bindings.{concept} requires table and sources")
    signatures = {(e["from"], e["type"], e["to"]) for e in graph["edges"]}
    for index, relationship in enumerate(relationships):
        if not isinstance(relationship, dict):
            errors.append(f"bindings.relationships[{index}] must be an object")
            continue
        signature = tuple(relationship.get(key) for key in ("from", "type", "to"))
        if signature not in signatures:
            errors.append(f"bindings.relationships[{index}] must reference a graph edge")
        joins = relationship.get("joins")
        if not isinstance(joins, list) or not joins:
            errors.append(f"bindings.relationships[{index}].joins must be nonempty")
            continue
        for join in joins:
            if not isinstance(join, dict) or any(not join.get(key) for key in ("from_table", "from_field", "to_table", "to_field", "constraint", "sources")):
                errors.append(f"bindings.relationships[{index}] has incomplete join")
    return errors


def validate_sources(graph, repo_root):
    errors = []
    sources = {
        source
        for entry in list(graph["nodes"].values()) + graph["edges"]
        for source in entry.get("sources", [])
    }
    for source in sorted(sources):
        path = Path(source)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"source must be repository-relative: {source}")
        elif not (repo_root / path).is_file():
            errors.append(f"source does not exist: {source}")
    return errors


def binding_sources(bindings):
    return {
        source
        for model_list in bindings["concepts"].values()
        for model in model_list
        for source in model.get("sources", [])
    } | {
        source
        for relationship in bindings["relationships"]
        for join in relationship.get("joins", [])
        for source in join.get("sources", [])
    }


def neighborhood(graph, name, depth):
    nodes = graph["nodes"]
    if name not in nodes:
        raise ValueError(f"unknown node: {name}")
    selected = {name}
    frontier = {name}
    included_edges = set()
    for _ in range(depth):
        next_frontier = set()
        for index, edge in enumerate(graph["edges"]):
            if edge["from"] in frontier or edge["to"] in frontier:
                included_edges.add(index)
                next_frontier.update((edge["from"], edge["to"]))
        frontier = next_frontier - selected
        selected |= next_frontier
    return {
        "nodes": {key: nodes[key] for key in sorted(selected)},
        "edges": [edge for index, edge in enumerate(graph["edges"]) if index in included_edges],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("validate", "show"))
    parser.add_argument("graph", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--bindings", type=Path)
    parser.add_argument("--entity")
    parser.add_argument("--depth", type=int, default=1)
    args = parser.parse_args()
    try:
        graph = load_graph(args.graph)
        errors = validate(graph)
        bindings = load_graph(args.bindings) if args.bindings else None
        if bindings is not None and not errors:
            errors.extend(validate_bindings(bindings, graph))
        if not errors and args.repo_root:
            errors.extend(validate_sources(graph, args.repo_root))
            if bindings is not None:
                for source in binding_sources(bindings):
                    path = Path(source)
                    if path.is_absolute() or ".." in path.parts or not (args.repo_root / path).is_file():
                        errors.append(f"binding source invalid: {source}")
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        if args.action == "validate":
            print(f"valid: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
        else:
            if not args.entity or args.depth < 0:
                parser.error("show requires --entity and nonnegative --depth")
            print(json.dumps(neighborhood(graph, args.entity, args.depth), indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
