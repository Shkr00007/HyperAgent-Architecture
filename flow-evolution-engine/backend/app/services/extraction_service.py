import json
import string
from typing import Any
from .ollama_client import OllamaClient


def _fallback_variant(label: str, strategy: str) -> dict[str, Any]:
    return {
        "strategy": strategy,
        "policies": ["safety_first", "concise_actions"],
        "tools": ["knowledge_lookup", "validator"],
        "sequencing_logic": "decision->action->verification",
        "nodes": [
            {"id": "start", "type": "decision", "label": f"Start {label}", "details": strategy},
            {"id": "analyze", "type": "action", "label": "Analyze Scenario", "details": "Extract constraints"},
            {"id": "tool", "type": "tool", "label": "Use Tool", "details": "Call helper"},
            {"id": "end", "type": "action", "label": "Finalize", "details": "Produce answer"},
        ],
        "edges": [
            {"source": "start", "target": "analyze", "condition": "always"},
            {"source": "analyze", "target": "tool", "condition": "needs_data"},
            {"source": "tool", "target": "end", "condition": "complete"},
        ],
        "entry_node": "start",
    }


def _default_variants(count: int) -> list[dict[str, Any]]:
    strategies = [
        "conservative risk-controlled planning",
        "speed-optimized direct resolution",
        "customer-empathy and negotiation-first",
    ]
    return [_fallback_variant(string.ascii_lowercase[i], strategies[i]) for i in range(count)]


def generate_flow_variants(text: str, variant_count: int) -> list[dict[str, Any]]:
    prompt = f"""
Generate exactly {variant_count} DIFFERENT decision workflows for this problem using different approaches.
Return valid JSON array. Each item MUST include:
- strategy
- prompt_strategy (how prompt style was framed)
- policies (array)
- tools (array)
- sequencing_logic
- nodes (decision/action/tool)
- edges
- entry_node
Problem text:\n{text[:14000]}
"""
    client = OllamaClient()
    fallback = _default_variants(variant_count)
    data = client.generate_json(prompt, fallback=fallback)

    if not isinstance(data, list) or len(data) < variant_count:
        return fallback

    cleaned = []
    for item in data[:variant_count]:
        if not isinstance(item, dict):
            continue
        required = ["nodes", "edges", "entry_node", "policies", "tools", "sequencing_logic"]
        if all(k in item for k in required):
            cleaned.append(item)
    return cleaned if len(cleaned) == variant_count else fallback


def mutate_winner_variants(parent_flow: dict[str, Any], meta_data: str) -> list[dict[str, Any]]:
    mutation_types = ["conservative", "aggressive", "hybrid"]
    prompt = f"""
Generate new flow variants, prioritizing strategies similar to high-performing past mutations: {meta_data}
Create exactly 3 improved versions of this workflow with diversity:
1) conservative variant
2) aggressive variant
3) hybrid variant
Return JSON array where each element has: mutation_type, strategy, prompt_strategy, policies, tools,
sequencing_logic, nodes, edges, entry_node.
Parent workflow JSON:\n{json.dumps(parent_flow)[:14000]}
"""

    fallback = []
    for i, m in enumerate(mutation_types, start=1):
        child = parent_flow.copy()
        child["mutation_type"] = m
        child["strategy"] = f"{m} mutation strategy"
        child["prompt_strategy"] = f"bias_toward_{m}"
        child["policies"] = list(dict.fromkeys([*(child.get("policies") or []), f"{m}_policy"]))
        fallback.append(child)

    client = OllamaClient()
    data = client.generate_json(prompt, fallback=fallback)
    if not isinstance(data, list) or len(data) < 3:
        return fallback

    normalized = []
    for i, m in enumerate(mutation_types):
        item = data[i] if isinstance(data[i], dict) else {}
        item["mutation_type"] = m
        normalized.append(item)
    return normalized
