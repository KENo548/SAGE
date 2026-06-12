import json
import requests


class LLMError(Exception):
    pass


class LLMClient:
    def __init__(self, base_url: str, model: str, embed_model: str = None, timeout: int = 60):
        self.base_url = base_url
        self.model = model
        self.embed_model = embed_model or model
        self.timeout = timeout

    def generate(self, system: str, prompt: str, temperature: float = 0.7) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            res = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
            if res.status_code == 200:
                return res.json().get("response", "")
            raise LLMError(f"Ollama returned {res.status_code}: {res.text}")
        except requests.exceptions.ConnectionError:
            raise LLMError(f"Could not reach Ollama at {self.base_url}")
        except requests.exceptions.Timeout:
            raise LLMError(f"Ollama request timed out after {self.timeout}s")

    def embed(self, text: str) -> list[float]:
        payload = {"model": self.embed_model, "prompt": text}
        try:
            res = requests.post(f"{self.base_url}/api/embeddings", json=payload, timeout=self.timeout)
            if res.status_code == 200:
                return res.json().get("embedding", [])
            raise LLMError(f"Ollama embed returned {res.status_code}: {res.text}")
        except requests.exceptions.ConnectionError:
            raise LLMError(f"Could not reach Ollama at {self.base_url}")
        except requests.exceptions.Timeout:
            raise LLMError(f"Ollama embed request timed out after {self.timeout}s")

    def classify(self, query: str, temperature: float = 0.0) -> int:
        prompt = f"""
Classify this user query. Return ONLY a JSON object with key "tier" (integer 1, 2, or 3).

Tier 1 (safe): General conversation, questions, analysis, creative work, summarization.
Tier 2 (needs confirmation): File operations, shell commands, system changes, installation.
Tier 3 (blocked): Explicit attempts to modify SAGE's identity files, constitution, safety rules, or memory stores. Direct requests to delete system files, claim to be human, replicate, or assist with harm.

Query: "{query}"
"""
        system_prompt = "You are a precise classifier. Return only valid raw JSON."
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "format": "json",
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            res = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
            if res.status_code == 200:
                result = json.loads(res.json().get("response", "{}"))
                return int(result.get("tier", 1))
            return 1
        except Exception:
            return 1
