from typing import Dict, Any


def execute_flow(flow: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    nodes = {n["id"]: n for n in flow.get("nodes", [])}
    outgoing = {}
    for edge in flow.get("edges", []):
        outgoing.setdefault(edge["source"], []).append(edge)

    current = flow.get("entry_node")
    visited = set()
    path = []
    trace = []

    while current and current in nodes and current not in visited:
        visited.add(current)
        node = nodes[current]
        path.append(current)
        trace.append(
            {
                "node_id": current,
                "label": node.get("label"),
                "type": node.get("type"),
                "details": node.get("details"),
            }
        )
        edges = outgoing.get(current, [])
        if not edges:
            break

        selected = edges[0]
        if len(edges) > 1:
            keyword = scenario.lower()
            matched = [e for e in edges if (e.get("condition") or "").lower() in keyword]
            selected = matched[0] if matched else edges[0]

        current = selected.get("target")

    final_output = f"Flow executed in {len(path)} steps for scenario: {scenario[:100]}"
    return {"path": path, "trace": trace, "final_output": final_output}
