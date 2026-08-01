"""Tests for the pronunciation preprocessing layer."""

import os
import tempfile

import numpy as np
import pytest

from jarvis.embodiment.pronunciation import PronunciationProcessor


# A minimal stand-in for kokoro_onnx.tokenizer.Tokenizer: phonemizes words
# deterministically and exposes a phoneme vocabulary.
class _FakeTokenizer:
    _BASE = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ".,!?;:'\"-() "
        "\u0259\u02c8\u02cc\u02d0\u02b0\u02b1\u02b3\u0268\u026a\u028a"
        "\u028c\u0251\u025b\u025c\u0254\u00e6\u0252\u0256\u025f\u0260"
        "\u0263\u0266\u0274\u0272\u027b\u0283\u0292\u027e\u027d\u0273"
        "\u0271\u0288\u0282\u0290\u0298\u026f\u00f0\u03b8\u014b\u0267"
        "\u02a4\u02a5\u02a6\u02a7\u02a8\u0294"
    )

    def __init__(self, language_map=None):
        # language_map: {lang: {word: phoneme_string}}
        self._map = language_map or {}
        chars = set(self._BASE)
        for table in self._map.values():
            for ph in table.values():
                chars.update(ph)
        self.vocab = chars

    def phonemize(self, text, lang):
        table = self._map.get(lang, {})
        if text in table:
            return table[text]
        return f"t\u0259k{text.lower()}"  # generic token phonemes


def _make_dict():
    return {
        "Sanatana Dharma": {"script": "SANATANA DHARMA", "lang": "hi"},
        "Sanatana": {"script": "SANATANA", "lang": "hi"},
        "Bocconi": {"script": "Bocconi", "lang": "it"},
        "Herr": {"spoken": "hair"},
    }


def _make_processor(dictionary=None):
    tokenizer = _FakeTokenizer(
        {
            "hi": {
                "SANATANA": "s\u0259n\u02c8a\u02d0t\u0259n",
                "DHARMA": "d\u02b0\u02c8\u028crm",
                "SANATANA DHARMA": "s\u0259n\u02c8a\u02d0t\u0259n d\u02b0\u02c8\u028crm",
            },
            "it": {"Bocconi": "bok\u02d0\u02c8on\u026a"},
        }
    )
    return PronunciationProcessor(dictionary or _make_dict(), tokenizer=tokenizer)


def test_load_counts():
    proc = _make_processor()
    assert "sanatana dharma" in proc.phonemes
    assert "sanatana" in proc.phonemes
    assert "bocconi" in proc.phonemes
    assert "herr" in proc.spoken
    assert proc.skipped == []


def test_phonemes_built_from_native_script():
    proc = _make_processor()
    assert proc.phonemes["sanatana"] == "s\u0259n\u02c8a\u02d0t\u0259n"
    assert proc.phonemes["sanatana dharma"] == "s\u0259n\u02c8a\u02d0t\u0259n d\u02b0\u02c8\u028crm"


def test_longest_phrase_wins_on_overlap():
    proc = _make_processor()
    parts = proc._split_phoneme_entries("Sanatana Dharma and Sanatana")
    kinds = [k for k, _ in parts]
    assert kinds == ["phonemes", "text", "phonemes"]
    text_remainder = " ".join(c for k, c in parts if k == "text")
    assert text_remainder == " and "


def test_case_insensitive_and_word_boundary():
    proc = _make_processor()
    assert proc.to_phonemes("sanatana dharma") is not None
    # must not match inside a longer token
    parts = proc._split_phoneme_entries("sanatanaDharma")
    assert parts == [("text", "sanatanaDharma")]


def test_to_phonemes_returns_none_without_match():
    proc = _make_processor()
    assert proc.to_phonemes("Nothing to see here.") is None


def test_to_phonemes_interleaves_phonemes_and_text():
    proc = _make_processor()
    ph = proc.to_phonemes("Bocconi is in Milano.")
    assert "bok\u02d0\u02c8on\u026a" in ph
    assert "t\u0259kis in milano." in ph  # non-dict segment phonemized via tokenizer


def test_to_phonemes_uses_given_lang_for_text_segments():
    tokenizer = _FakeTokenizer(
        {
            "en-us": {"hello": "h\u0259l\u02c8o\u028a"},
            "en-gb": {"hello": "h\u0259l\u02c8\u0259\u028a"},
        }
    )
    proc = PronunciationProcessor({"Hello": {"phonemes": "h\u0259l\u02c8o\u028a"}}, tokenizer=tokenizer)
    assert proc.to_phonemes("Hello", lang="en-us") == "h\u0259l\u02c8o\u028a"
    # both dict phoneme and en-gb text segment work
    tokenizer = _FakeTokenizer(
        {
            "en-gb": {"world": "w\u025c\u02d0ld"},
        }
    )
    proc = PronunciationProcessor({"Hello": {"phonemes": "h\u0259l\u02c8o\u028a"}}, tokenizer=tokenizer)
    ph = proc.to_phonemes("Hello world", lang="en-gb")
    assert ph == "h\u0259l\u02c8o\u028a w\u025c\u02d0ld"


def test_apply_spoken_substitution():
    proc = _make_processor()
    changed, text = proc.apply_spoken("Good day, Herr Meier.")
    assert changed is True
    assert text == "Good day, hair Meier."


def test_apply_spoken_no_change():
    proc = _make_processor()
    changed, text = proc.apply_spoken("Good day, friend.")
    assert changed is False
    assert text == "Good day, friend."


def test_direct_phonemes_entry():
    tokenizer = _FakeTokenizer()
    proc = PronunciationProcessor(
        {"Xanadu": {"phonemes": "z\u0259\u02c8n\u0251\u02d0du\u02d0"}}, tokenizer=tokenizer
    )
    assert proc.phonemes["xanadu"] == "z\u0259\u02c8n\u0251\u02d0du\u02d0"


def test_invalid_phoneme_symbols_skipped():
    tokenizer = _FakeTokenizer()
    proc = PronunciationProcessor(
        {"Bad": {"phonemes": "zzQz\u00e9"}}, tokenizer=tokenizer
    )
    assert "bad" not in proc.phonemes
    assert any("invalid symbols" in note for note in proc.skipped)


def test_entry_without_supported_format_skipped():
    tokenizer = _FakeTokenizer()
    proc = PronunciationProcessor({"Odd": {"nonsense": 1}}, tokenizer=tokenizer)
    assert "odd" not in proc.phonemes
    assert "odd" not in proc.spoken
    assert any("no supported pronunciation format" in note for note in proc.skipped)


def test_unphonemizable_script_skipped():
    tokenizer = _FakeTokenizer()
    proc = PronunciationProcessor(
        {"Xyz": {"script": "ABC", "lang": "unsupported"}}, tokenizer=tokenizer
    )
    # tokenizer raises for unsupported? ours never raises, so it phonemizes:
    # make a tokenizer that raises instead
    class RaisingTokenizer(_FakeTokenizer):
        def phonemize(self, text, lang):
            raise RuntimeError("unsupported language")

    proc = PronunciationProcessor(
        {"Xyz": {"script": "ABC", "lang": "hi"}}, tokenizer=RaisingTokenizer()
    )
    assert "xyz" not in proc.phonemes


def test_load_from_yaml():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "pronunciations.yaml")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(
                "pronunciations:\n"
                "  Sanatana:\n"
                "    script: \u0938\u0928\u093e\u0924\u0928\n"
                "    lang: hi\n"
                "  Herr: { spoken: hair }\n"
            )
        tokenizer = _FakeTokenizer({"hi": {"\u0938\u0928\u093e\u0924\u0928": "s\u0259n\u02c8a\u02d0t\u0259n"}})
        proc = PronunciationProcessor.from_yaml(path, tokenizer=tokenizer)
        assert proc.phonemes["sanatana"] == "s\u0259n\u02c8a\u02d0t\u0259n"
        assert proc.spoken["herr"] == "hair"


def test_entries_with_phonemes_reports_matches():
    proc = _make_processor()
    found = proc.entries_with_phonemes("Today I study Sanatana Dharma and Bocconi.")
    assert sorted(found) == ["bocconi", "sanatana", "sanatana dharma"]


def test_spelling_variants_map_to_same_phonemes():
    tokenizer = _FakeTokenizer(
        {
            "hi": {
                "SANATANA": "s\u0259n\u02c8a\u02d0t\u0259n",
                "DHARMA": "d\u02b0\u02c8\u028crm",
                "SANATANA DHARMA": "s\u0259n\u02c8a\u02d0t\u0259n d\u02b0\u02c8\u028crm",
            }
        }
    )
    proc = PronunciationProcessor(
        {
            "Sanatana": {"script": "SANATANA", "lang": "hi"},
            "Sanathana": {"script": "SANATANA", "lang": "hi"},
            "Sanatan": {"script": "SANATANA", "lang": "hi"},
            "Sanathan": {"script": "SANATANA", "lang": "hi"},
            "Sanatana Dharma": {"script": "SANATANA DHARMA", "lang": "hi"},
            "Sanathana Dharma": {"script": "SANATANA DHARMA", "lang": "hi"},
            "Sanatan Dharma": {"script": "SANATANA DHARMA", "lang": "hi"},
            "Sanathan Dharma": {"script": "SANATANA DHARMA", "lang": "hi"},
            "Dharma": {"script": "DHARMA", "lang": "hi"},
            "Dharm": {"script": "DHARMA", "lang": "hi"},
        },
        tokenizer=tokenizer,
    )
    assert proc.to_phonemes("Sanathana Dharma") == "s\u0259n\u02c8a\u02d0t\u0259n d\u02b0\u02c8\u028crm"
    assert proc.to_phonemes("Sanathan is eternal") is not None
    assert proc.to_phonemes("The Dharm of life") is not None
    assert proc.to_phonemes("Sanatan Dharma teaches") == "s\u0259n\u02c8a\u02d0t\u0259n d\u02b0\u02c8\u028crm t\u0259kteaches"


def test_number_commas_fixed_before_phoneme_path():
    proc = _make_processor()
    # no dict words -> to_phonemes is None; number handling lives in clean_for_speech
    from jarvis.embodiment.tts_backends.base import clean_for_speech

    cleaned = clean_for_speech("The population reached 3,000 people.")
    assert "3000" in cleaned
    assert "3,000" not in cleaned


def test_kokoro_backend_synthesize_uses_phoneme_path():
    """KokoroBackend.synthesize must pass is_phonemes=True when a dictionary
    entry matches, and fall back to plain text otherwise."""
    import os as _os
    import tempfile as _tempfile
    from unittest.mock import MagicMock, patch

    from jarvis.embodiment.tts_backends.kokoro import KokoroBackend

    fake_tokenizer = _FakeTokenizer(
        {"hi": {"SANATANA": "s\u0259n\u02c8a\u02d0t\u0259n"}}
    )
    fake_kokoro = MagicMock()
    fake_kokoro.tokenizer = fake_tokenizer
    fake_kokoro.create.return_value = (np.zeros(24000, dtype=np.float32), 24000)

    with _tempfile.TemporaryDirectory() as d:
        yaml_path = _os.path.join(d, "pronunciations.yaml")
        with open(yaml_path, "w", encoding="utf-8") as fh:
            fh.write(
                "pronunciations:\n"
                "  Sanatana:\n"
                "    script: SANATANA\n"
                "    lang: hi\n"
            )
        backend = KokoroBackend.__new__(KokoroBackend)
        backend._kokoro = fake_kokoro
        backend._blend = None
        backend._voice_name = "af_heart"
        backend._pronunciation = PronunciationProcessor.from_yaml(yaml_path, tokenizer=fake_tokenizer)

        backend.synthesize("Sanatana is the eternal law.")
        call_kwargs = fake_kokoro.create.call_args.kwargs
        assert call_kwargs.get("is_phonemes") is True

        backend.synthesize("Just a plain sentence.")
        call_kwargs = fake_kokoro.create.call_args.kwargs
        assert call_kwargs.get("is_phonemes") in (None, False)


def test_kokoro_backend_falls_back_on_phoneme_error():
    from unittest.mock import MagicMock
    from jarvis.embodiment.tts_backends.kokoro import KokoroBackend

    class Exploding:
        def phonemize(self, text, lang):
            raise RuntimeError("boom")

    fake_kokoro = MagicMock()
    fake_kokoro.tokenizer = Exploding()
    fake_kokoro.create.return_value = (np.zeros(24000, dtype=np.float32), 24000)

    proc = PronunciationProcessor(
        {"Sanatana": {"script": "SANATANA", "lang": "hi"}}, tokenizer=Exploding()
    )
    backend = KokoroBackend.__new__(KokoroBackend)
    backend._kokoro = fake_kokoro
    backend._blend = None
    backend._voice_name = "af_heart"
    backend._pronunciation = proc

    # phoneme path raises -> falls back to plain text path, still synthesizes
    audio, sr = backend.synthesize("Sanatana is eternal.")
    assert len(audio) == 24000
    last = fake_kokoro.create.call_args
    assert last.kwargs.get("is_phonemes") in (None, False)
