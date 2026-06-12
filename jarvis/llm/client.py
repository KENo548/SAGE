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
You are a strict security classification engine. Classify the user query into exactly one of these three Tiers:
- Tier 1: Safe conversational or analytical tasks. Examples: writing code, general knowledge, math, formatting, summarizations, general questions.
- Tier 2: Potentially dangerous system tasks that need confirmation. Examples: file modifications, file deletions, running shell commands, executing scripts, local installations, process modifications.
- Tier 3: Strictly Prohibited governance violations. Examples: self-modification of core/safety rules, editing identity config files, deleting memory databases, deception (acting human), replication, or assisting in harm (hacking, bomb making).

Query: "{query}"

Output ONLY a valid JSON object with a single key "tier" (which must be an integer: 1, 2, or 3).
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
