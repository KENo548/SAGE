from jarvis.identity.loader import IdentityLoader
from jarvis.identity.models import Identity, Constitution


def test_load_identity():
    loader = IdentityLoader(soul_path="data/soul", constitution_path="data/constitution")
    identity = loader.load()
    assert isinstance(identity, Identity)
    assert identity.name == "SAGE"
    assert identity.codename == "jarvis"
    assert identity.purpose
    assert identity.genesis_text


def test_load_constitution():
    loader = IdentityLoader(soul_path="data/soul", constitution_path="data/constitution")
    constitution = loader.load_constitution()
    assert isinstance(constitution, Constitution)
    assert len(constitution.core_rules) > 0
    assert len(constitution.safety_rules) > 0
    for rule in constitution.core_rules:
        assert rule.id.startswith("CR_")
        assert rule.tier in (1, 2, 3)


def test_reload():
    loader = IdentityLoader(soul_path="data/soul", constitution_path="data/constitution")
    identity1 = loader.load()
    loader.reload()
    identity2 = loader.load()
    assert identity1.name == identity2.name


def test_missing_file_raises():
    loader = IdentityLoader(soul_path="data/soul", constitution_path="nonexistent")
    try:
        loader.load_constitution()
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass
