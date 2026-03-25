import json
import os
import requests


class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://ollama-mobius-sales.mobiusdtaas.ai/").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3:instruct")

    def generate_json(self, prompt: str, fallback: dict) -> dict:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        try:
            r = requests.post(url, json=payload, timeout=60)
            r.raise_for_status()
            response = r.json().get("response", "{}")
            return json.loads(response)
        except Exception:
            return fallback
