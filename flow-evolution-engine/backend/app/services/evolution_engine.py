from collections import defaultdict
from typing import Any


def select_top_flows(scored_items: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    return sorted(scored_items, key=lambda x: x.get("score", 0.0), reverse=True)[:top_k]


def mutation_insights(history_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets = defaultdict(list)
    for row in history_rows:
        buckets[row["mutation_type"]].append(row.get("performance_delta", 0.0))

    insights = []
    for mtype, vals in buckets.items():
        insights.append({"mutation_type": mtype, "avg_delta": round(sum(vals) / len(vals), 4), "uses": len(vals)})
    return sorted(insights, key=lambda x: x["avg_delta"], reverse=True)


def build_meta_bias(meta_rows: list[dict[str, Any]]) -> str:
    if not meta_rows:
        return "No meta history yet. Keep balanced diversity."
    ranked = sorted(meta_rows, key=lambda r: (r.get("success_rate", 0), r.get("avg_score", 0)), reverse=True)
    top = ranked[:3]
    return "; ".join([
        f"{t['mutation_type']} avg_score={t['avg_score']:.3f} success_rate={t['success_rate']:.2f}"
        for t in top
    ])


def summarize_structure_patterns(flows: list[dict[str, Any]]) -> str:
    if not flows:
        return "No structure patterns yet."
    node_counts = [len(f.get("nodes", [])) for f in flows]
    policy_counts = [len(f.get("policies", [])) for f in flows]
    return (
        f"winning_structures avg_nodes={sum(node_counts)/len(node_counts):.2f}, "
        f"avg_policies={sum(policy_counts)/len(policy_counts):.2f}"
    )
