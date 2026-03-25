from typing import Dict, Any


def execute_flow(flow: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    nodes = {n["id"]: n for n in flow.get("nodes", [])}
    outgoing = {}
    for edge in flow.get("edges", []):
        outgoing.setdefault(edge["source"], []).append(edge)

    current = flow.get("entry_node")
    path = []
    trace = []
    visited = set()

    while current and current in nodes and current not in visited:
        visited.add(current)
        node = nodes[current]
        path.append(current)

        trace.append(
            {
                "node_id": current,
                "label": node.get("label"),
                "type": node.get("type"),
                "policy_context": flow.get("policies", []),
                "tool_context": flow.get("tools", []),
            }
        )

        next_edges = outgoing.get(current, [])
        if not next_edges:
            break

        selected = next_edges[0]
        if len(next_edges) > 1:
            scenario_l = scenario.lower()
            weighted = sorted(
                next_edges,
                key=lambda e: int((e.get("condition") or "").lower() in scenario_l),
                reverse=True,
            )
            selected = weighted[0]

        current = selected.get("target")

    output_text = (
        f"strategy={flow.get('strategy', 'unknown')} | "
        f"policies={','.join(flow.get('policies', []))} | "
        f"steps={len(path)} | scenario={scenario[:120]}"
    )

    return {"path": path, "trace": trace, "output_text": output_text}
