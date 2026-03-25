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
        insights.append(
            {
                "mutation_type": mtype,
                "avg_delta": round(sum(vals) / len(vals), 4),
                "uses": len(vals),
            }
        )
    return sorted(insights, key=lambda x: x["avg_delta"], reverse=True)


def build_mutation_guidance(insights: list[dict[str, Any]]) -> str:
    if not insights:
        return "No prior history. Try diverse structural mutations and policy changes."

    top = insights[:3]
    parts = [f"{i['mutation_type']} (avg_delta={i['avg_delta']}, uses={i['uses']})" for i in top]
    return "Prefer mutation styles with highest historical delta: " + "; ".join(parts)
