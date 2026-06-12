from typing import Optional

from jarvis.capabilities.base import Capability

REGISTRY: dict[str, Capability] = {}


def register_capability(cap: Capability) -> None:
    REGISTRY[cap.id] = cap


def get_capability(cap_id: str) -> Optional[Capability]:
    return REGISTRY.get(cap_id)
