from typing import Any, Dict
from .ollama_client import OllamaClient


def _keyword_signal(output_text: str, scenario: str) -> float:
    scenario_words = {w for w in scenario.lower().split() if len(w) > 4}
    output_words = set(output_text.lower().split())
    if not scenario_words:
        return 0.3
    overlap = len(scenario_words.intersection(output_words)) / len(scenario_words)
    return min(max(overlap, 0.0), 1.0)


def _goal_success_sim(flow: Dict[str, Any], execution_output: Dict[str, Any]) -> float:
    expected_tools = len(flow.get("tools", [])) or 1
    used_steps = len(execution_output.get("path", []))
    return min(used_steps / (expected_tools + 2), 1.0)


def _llm_quality_score(scenario: str, output_text: str) -> float:
    client = OllamaClient()
    prompt = f"""
Score this workflow output quality for scenario on scale 0 to 1.
Return JSON: {{"quality": number, "reason": "short"}}
Scenario: {scenario}
Output: {output_text}
"""
    result = client.generate_json(prompt, fallback={"quality": 0.5, "reason": "fallback"})
    try:
        q = float(result.get("quality", 0.5))
        return max(0.0, min(1.0, q))
    except Exception:
        return 0.5


def evaluate_execution(flow: Dict[str, Any], execution_output: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    keyword = _keyword_signal(execution_output.get("output_text", ""), scenario)
    goal_success = _goal_success_sim(flow, execution_output)
    llm_quality = _llm_quality_score(scenario, execution_output.get("output_text", ""))

    score = round((0.45 * llm_quality) + (0.35 * keyword) + (0.20 * goal_success), 4)
    signals = {
        "llm_quality": llm_quality,
        "keyword_signal": keyword,
        "goal_success": goal_success,
    }
    notes = (
        f"Composite from llm_quality={llm_quality:.3f}, "
        f"keyword_signal={keyword:.3f}, goal_success={goal_success:.3f}"
    )

    return {"score": score, "signals": signals, "notes": notes}
