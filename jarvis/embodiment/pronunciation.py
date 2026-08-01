"""Pronunciation preprocessing layer for TTS.

SAGE's text-to-speech runs on Kokoro, an English-focused model. English
phonemization mangles foreign and proper nouns ("Sanatana" -> "suntana").
This module sits between the response text and the synthesizer: it looks up
known words and phrases in a pronunciation dictionary and either

  * substitutes a plain-text respelling, or
  * produces an exact phoneme string that Kokoro synthesizes verbatim
    (via Kokoro.create(..., is_phonemes=True)).

The dictionary lives in data/pronunciations/pronunciations.yaml and is
user-editable. Native-script entries (e.g. Devanagari for Sanskrit) are
phonemized with their own language so the pronunciation is authentic.
"""

import re
from typing import Optional

import yaml


_LANG_MARKER = re.compile(r"\((en|hi|mr|bn|gu|kn|ml|pa|te|ta|ur|ne|si|it|de|es|ja|ko|ru|pt|nl|pl|tr|el)\)")


class PronunciationProcessor:
    """Applies the pronunciation dictionary to text destined for TTS.

    Attributes:
        spoken: map of lowercased phrase -> plain-text substitution.
        phonemes: map of lowercased phrase -> exact phoneme string.
    """

    def __init__(self, dictionary: Optional[dict] = None, tokenizer=None) -> None:
        self._tokenizer = tokenizer
        self.spoken: dict[str, str] = {}
        self.phonemes: dict[str, str] = {}
        self._skipped: list[str] = []
        if dictionary:
            self.load(dictionary)

    # ── construction ──────────────────────────────────────────────────────

    @classmethod
    def from_yaml(cls, path: str, tokenizer=None) -> "PronunciationProcessor":
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        entries = (data or {}).get("pronunciations", {}) or {}
        return cls(entries, tokenizer=tokenizer)

    def load(self, dictionary: dict) -> None:
        for phrase, spec in dictionary.items():
            try:
                self._add_entry(str(phrase), spec)
            except Exception as exc:  # noqa: BLE001 - one bad entry must not sink the load
                self._skipped.append(f"{phrase}: {exc}")

    def _add_entry(self, phrase: str, spec) -> None:
        key = phrase.lower().strip()
        if not key:
            return

        if isinstance(spec, str):
            self.spoken[key] = spec
            return

        if not isinstance(spec, dict):
            return

        if "spoken" in spec:
            self.spoken[key] = str(spec["spoken"])
            return

        if "phonemes" in spec:
            ph = str(spec["phonemes"])
            if self._validate_phonemes(phrase, ph):
                self.phonemes[key] = ph
            return

        script = spec.get("script")
        lang = spec.get("lang")
        if script and lang and self._tokenizer is not None:
            ph = self._phonemize(str(script), str(lang))
            if ph:
                if self._validate_phonemes(phrase, ph):
                    self.phonemes[key] = ph
            else:
                self._skipped.append(f"{phrase}: could not phonemize {script!r} in {lang}")
            return

        self._skipped.append(f"{phrase}: no supported pronunciation format")

    def _phonemize(self, text: str, lang: str) -> Optional[str]:
        try:
            ph = self._tokenizer.phonemize(text, lang)
        except Exception:  # noqa: BLE001 - language may be unsupported on this machine
            return None
        if not ph:
            return None
        return _LANG_MARKER.sub("", ph).strip()

    def _validate_phonemes(self, phrase: str, ph: str) -> bool:
        """Return True if every symbol in `ph` is in the phoneme vocabulary.

        Appends a skip note when invalid symbols are found so callers can
        report the entry without keeping it.
        """
        vocab = getattr(self._tokenizer, "vocab", None)
        if not vocab:
            return True
        invalid = sorted({c for c in ph if c not in vocab and not c.isspace()})
        if invalid:
            self._skipped.append(f"{phrase}: phonemes contain invalid symbols {invalid}")
            return False
        return True

    @property
    def skipped(self) -> list[str]:
        return list(self._skipped)

    # ── application ───────────────────────────────────────────────────────

    def apply_spoken(self, text: str) -> tuple[bool, str]:
        """Apply plain-text respelling substitutions. Returns (changed, text)."""
        if not self.spoken:
            return False, text
        changed = False
        for key, replacement in self.spoken.items():
            pattern = re.compile(rf"(?<!\w){re.escape(key)}(?!\w)", re.IGNORECASE)
            if pattern.search(text):
                text = pattern.sub(replacement, text)
                changed = True
        return changed, text

    def _split_phoneme_entries(self, text: str) -> list[tuple[str, str]]:
        """Split text into (kind, content) parts around phoneme-dictionary matches.

        kind is "phonemes" for dictionary entries and "text" for everything
        else. Longest phrases match first; overlapping shorter phrases are
        skipped so the longest spelling wins.
        """
        if not self.phonemes:
            return [("text", text)]

        matches: list[tuple[int, int, str]] = []
        for phrase in sorted(self.phonemes, key=len, reverse=True):
            pattern = re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", re.IGNORECASE)
            for m in pattern.finditer(text):
                matches.append((m.start(), m.end(), self.phonemes[phrase]))

        if not matches:
            return [("text", text)]

        matches.sort(key=lambda m: (m[0], -(m[1] - m[0])))
        kept: list[tuple[int, int, str]] = []
        for start, end, ph in matches:
            if kept and start < kept[-1][1]:
                continue
            kept.append((start, end, ph))

        parts: list[tuple[str, str]] = []
        pos = 0
        for start, end, ph in kept:
            if start > pos:
                parts.append(("text", text[pos:start]))
            parts.append(("phonemes", ph))
            pos = end
        if pos < len(text):
            parts.append(("text", text[pos:]))
        return parts

    def to_phonemes(self, text: str, lang: str = "en-us") -> Optional[str]:
        """Build a full phoneme string for `text`.

        Returns None when no phoneme-dictionary entry is present, in which
        case the caller should synthesize `text` normally.
        """
        if not self.phonemes or self._tokenizer is None:
            return None

        parts = self._split_phoneme_entries(text)
        has_phonemes = any(kind == "phonemes" for kind, _ in parts)
        if not has_phonemes:
            return None

        out: list[str] = []
        for kind, content in parts:
            if kind == "phonemes":
                out.append(content)
                continue
            stripped = content.strip()
            if not stripped:
                continue
            ph = self._phonemize(stripped, lang)
            if not ph:
                return None
            out.append(ph)

        joined = " ".join(p for p in out if p)
        return joined.strip() or None

    def entries_with_phonemes(self, text: str) -> list[str]:
        """Names of phoneme-dictionary phrases present in `text` (for logging)."""
        found: list[str] = []
        for phrase, ph in self.phonemes.items():
            if re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text, re.IGNORECASE):
                found.append(phrase)
        return found
