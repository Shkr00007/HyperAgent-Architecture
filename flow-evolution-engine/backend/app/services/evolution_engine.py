import copy
from typing import Dict, Any


def evolve_flow(flow: Dict[str, Any], prior_score: float) -> Dict[str, Any]:
    new_flow = copy.deepcopy(flow)
    node_id = f"opt_{len(new_flow.get('nodes', [])) + 1}"
    new_node = {
        "id": node_id,
        "type": "action",
        "label": "Optimization Step",
        "details": "Inserted by HyperAgent evolution loop",
    }

    nodes = new_flow.setdefault("nodes", [])
    edges = new_flow.setdefault("edges", [])
    if nodes:
        last_id = nodes[-1]["id"]
        edges.append({"source": last_id, "target": node_id, "condition": "optimize"})
    nodes.append(new_node)

    return {
        "flow": new_flow,
        "reason": f"Added optimization node to improve reliability from score {prior_score:.3f}",
    }
