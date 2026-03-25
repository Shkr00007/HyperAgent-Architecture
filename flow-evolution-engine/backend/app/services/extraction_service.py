import json
from .ollama_client import OllamaClient


DEFAULT_FLOW = {
    "nodes": [
        {"id": "start", "type": "decision", "label": "Start", "details": "Begin flow"},
        {"id": "review", "type": "action", "label": "Review Input", "details": "Inspect scenario context"},
        {"id": "decide", "type": "decision", "label": "Decision", "details": "Choose best path"},
        {"id": "end", "type": "action", "label": "Finish", "details": "Return result"},
    ],
    "edges": [
        {"source": "start", "target": "review", "condition": "always"},
        {"source": "review", "target": "decide", "condition": "ready"},
        {"source": "decide", "target": "end", "condition": "selected"},
    ],
    "entry_node": "start",
}


def extract_flow_from_text(text: str) -> dict:
    prompt = f"""
Extract a decision flow as JSON with this exact shape:
{{
  "nodes": [{{"id":"string","type":"decision|action","label":"string","details":"string"}}],
  "edges": [{{"source":"node_id","target":"node_id","condition":"string"}}],
  "entry_node": "node_id"
}}
Text:\n{text[:12000]}
Return only valid JSON.
"""
    client = OllamaClient()
    flow = client.generate_json(prompt, fallback=DEFAULT_FLOW)

    if not isinstance(flow, dict) or "nodes" not in flow or "edges" not in flow:
        flow = DEFAULT_FLOW

    try:
        json.dumps(flow)
    except Exception:
        flow = DEFAULT_FLOW
    return flow
