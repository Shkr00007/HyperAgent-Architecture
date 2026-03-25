from typing import Dict, Any


def evaluate_execution(flow: Dict[str, Any], execution_output: Dict[str, Any]) -> Dict[str, Any]:
    total_nodes = max(len(flow.get("nodes", [])), 1)
    traversed = len(execution_output.get("path", []))
    coverage = min(traversed / total_nodes, 1.0)
    score = round(0.6 + 0.4 * coverage, 3)
    notes = f"Coverage={coverage:.2f}; traversed {traversed}/{total_nodes} nodes"
    return {"score": score, "notes": notes}
