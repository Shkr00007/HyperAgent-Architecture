import json
import os
import requests


class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://ollama-mobius-sales.mobiusdtaas.ai/").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3:instruct")

    def _generate(self, prompt: str, fmt: str | None = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if fmt:
            payload["format"] = fmt
        r = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=90)
        r.raise_for_status()
        return r.json().get("response", "")

    def generate_text(self, prompt: str, fallback: str = "") -> str:
        try:
            return self._generate(prompt)
        except Exception:
            return fallback

    def generate_json(self, prompt: str, fallback: dict | list):
        try:
            text = self._generate(prompt, fmt="json")
            return json.loads(text)
        except Exception:
            return fallback
