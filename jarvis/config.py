import os
import yaml
from dataclasses import dataclass, field


@dataclass
class Config:
    models: dict = field(default_factory=lambda: {
        "primary": "llama3.2:latest",
        "embedding": "nomic-embed-text:latest",
        "ollama_url": "http://localhost:11434",
    })
    identity: dict = field(default_factory=lambda: {
        "soul_path": "data/soul",
        "constitution_path": "data/constitution",
    })
    memory: dict = field(default_factory=lambda: {
        "chroma_db_path": "data/chroma_db",
        "retrieval": {"top_k_episodic": 5, "top_k_knowledge": 5},
        "candidate_cleanup_days": 30,
    })
    governance: dict = field(default_factory=lambda: {
        "llm_timeout": 60,
        "temperature": 0.0,
    })
    context: dict = field(default_factory=lambda: {
        "default_budget": 2000,
    })
    promotion: dict = field(default_factory=lambda: {
        "threshold": 0.65,
        "min_cluster_size": 3,
        "supersession_threshold": 0.85,
    })
    llm: dict = field(default_factory=lambda: {
        "default_timeout": 120,
        "temperature": 0.7,
    })


def load_config(path: str) -> Config:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config(
        models=data.get("models", Config.models),
        identity=data.get("identity", Config.identity),
        memory=data.get("memory", Config.memory),
        governance=data.get("governance", Config.governance),
        context=data.get("context", Config.context),
        promotion=data.get("promotion", Config.promotion),
        llm=data.get("llm", Config.llm),
    )
