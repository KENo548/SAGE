from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Identity:
    name: str
    codename: str
    role: str
    purpose: str
    version: str
    traits: dict = field(default_factory=dict)
    preferences: dict = field(default_factory=dict)
    personality_style: dict = field(default_factory=dict)
    quirks: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    soul: dict = field(default_factory=dict)
    genesis_text: str = ""


@dataclass
class ConstitutionalRule:
    id: str
    description: str
    tier: int
    category: str


@dataclass
class Constitution:
    schema_version: int = 1
    core_rules: list[ConstitutionalRule] = field(default_factory=list)
    safety_rules: list[ConstitutionalRule] = field(default_factory=list)
