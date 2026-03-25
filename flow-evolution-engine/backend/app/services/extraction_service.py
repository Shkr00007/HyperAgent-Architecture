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
        "cost-minimization with escalation gating",
        "tool-heavy evidence-first arbitration",
        "policy-strict deterministic handling",
    ]
    variants = []
    for i in range(count):
        variants.append(_fallback_variant(string.ascii_lowercase[i], strategies[i]))
    return variants


def generate_flow_variants(text: str, variant_count: int) -> list[dict[str, Any]]:
    prompt = f"""
Generate {variant_count} DIFFERENT decision workflows for this problem using different approaches.
Return valid JSON array. Each item MUST include:
- strategy
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

    if len(cleaned) < variant_count:
        return fallback

    json.dumps(cleaned)
    return cleaned


def mutate_winner_variants(parent_flow: dict[str, Any], mutation_guidance: str, children: int) -> list[dict[str, Any]]:
    prompt = f"""
Create {children} improved versions of this workflow using different strategies.
Use this mutation guidance from prior wins: {mutation_guidance}
Parent workflow JSON:\n{json.dumps(parent_flow)[:14000]}
Return JSON array with each child containing: mutation_type, strategy, policies, tools,
sequencing_logic, nodes, edges, entry_node.
"""
    client = OllamaClient()
    fallback = []
    for i in range(children):
        child = parent_flow.copy()
        child["mutation_type"] = f"heuristic_mutation_{i+1}"
        child["strategy"] = f"mutated strategy {i+1}"
        child["policies"] = list(dict.fromkeys([*(child.get("policies") or []), f"mutation_policy_{i+1}"]))
        fallback.append(child)

    data = client.generate_json(prompt, fallback=fallback)
    if not isinstance(data, list) or len(data) < children:
        return fallback
    return data[:children]
