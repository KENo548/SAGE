import os
import yaml
from dataclasses import dataclass, field

DEFAULT_MODELS = {
    "primary": "llama3.2:latest",
    "embedding": "nomic-embed-text:latest",
    "ollama_url": "http://localhost:11434",
}
DEFAULT_IDENTITY = {
    "soul_path": "data/soul",
    "constitution_path": "data/constitution",
}
DEFAULT_MEMORY = {
    "chroma_db_path": "data/chroma_db",
    "retrieval": {"top_k_episodic": 5, "top_k_knowledge": 5},
    "candidate_cleanup_days": 30,
}
DEFAULT_GOVERNANCE = {
    "llm_timeout": 60,
    "temperature": 0.0,
}
DEFAULT_CONTEXT = {
    "default_budget": 2000,
}
DEFAULT_PROMOTION = {
    "threshold": 0.65,
    "min_cluster_size": 3,
    "supersession_threshold": 0.85,
}
DEFAULT_LLM = {
    "default_timeout": 120,
    "temperature": 0.7,
}


@dataclass
class Config:
    models: dict = field(default_factory=lambda: dict(DEFAULT_MODELS))
    identity: dict = field(default_factory=lambda: dict(DEFAULT_IDENTITY))
    memory: dict = field(default_factory=lambda: dict(DEFAULT_MEMORY))
    governance: dict = field(default_factory=lambda: dict(DEFAULT_GOVERNANCE))
    context: dict = field(default_factory=lambda: dict(DEFAULT_CONTEXT))
    promotion: dict = field(default_factory=lambda: dict(DEFAULT_PROMOTION))
    llm: dict = field(default_factory=lambda: dict(DEFAULT_LLM))


def load_config(path: str) -> Config:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config(
        models=data.get("models", dict(DEFAULT_MODELS)),
        identity=data.get("identity", dict(DEFAULT_IDENTITY)),
        memory=data.get("memory", dict(DEFAULT_MEMORY)),
        governance=data.get("governance", dict(DEFAULT_GOVERNANCE)),
        context=data.get("context", dict(DEFAULT_CONTEXT)),
        promotion=data.get("promotion", dict(DEFAULT_PROMOTION)),
        llm=data.get("llm", dict(DEFAULT_LLM)),
    )
