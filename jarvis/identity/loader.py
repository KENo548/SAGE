import os
import yaml
from jarvis.identity.models import Identity, Constitution, ConstitutionalRule


class IdentityLoader:
    def __init__(self, soul_path: str, constitution_path: str):
        self.soul_path = soul_path
        self.constitution_path = constitution_path
        self._identity_cache: Identity | None = None
        self._constitution_cache: Constitution | None = None

    def load(self) -> Identity:
        if self._identity_cache is not None:
            return self._identity_cache

        identity_path = os.path.join(self.soul_path, "identity.yaml")
        personality_path = os.path.join(self.soul_path, "personality.yaml")
        soul_path_file = os.path.join(self.soul_path, "soul.yaml")
        genesis_path = os.path.join(self.soul_path, "genesis.md")

        identity_data = self._load_yaml(identity_path)
        personality_data = self._load_yaml(personality_path)

        soul_data = {}
        if os.path.exists(soul_path_file):
            soul_data = self._load_yaml(soul_path_file)

        genesis_text = ""
        if os.path.exists(genesis_path):
            with open(genesis_path, "r", encoding="utf-8") as f:
                genesis_text = f.read()

        ident = identity_data.get("identity", {})

        self._identity_cache = Identity(
            name=ident.get("name", "SAGE"),
            codename=ident.get("codename", "jarvis"),
            role=ident.get("role", ""),
            purpose=ident.get("purpose", ""),
            version=ident.get("version", "0.1.0"),
            traits=ident.get("traits", {}),
            preferences=ident.get("preferences", {}),
            personality_style=personality_data.get("style", {}),
            quirks=personality_data.get("quirks", []),
            values=personality_data.get("values", []),
            limitations=personality_data.get("limitations", []),
            conversation_behavior=personality_data.get("conversation_behavior", {}),
            soul=soul_data,
            genesis_text=genesis_text,
        )
        return self._identity_cache

    def load_constitution(self) -> Constitution:
        if self._constitution_cache is not None:
            return self._constitution_cache

        constitution_path = os.path.join(self.constitution_path, "constitution.yaml")
        data = self._load_yaml(constitution_path)

        core_rules = [
            ConstitutionalRule(id=r["id"], description=r["description"], tier=r["tier"], category=r.get("category", ""))
            for r in data.get("core_rules", [])
        ]
        safety_rules = [
            ConstitutionalRule(id=r["id"], description=r["description"], tier=r["tier"], category=r.get("category", ""))
            for r in data.get("safety_rules", [])
        ]

        self._constitution_cache = Constitution(
            schema_version=data.get("schema_version", 1),
            core_rules=core_rules,
            safety_rules=safety_rules,
        )
        return self._constitution_cache

    def reload(self) -> None:
        self._identity_cache = None
        self._constitution_cache = None

    @staticmethod
    def _load_yaml(path: str) -> dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
