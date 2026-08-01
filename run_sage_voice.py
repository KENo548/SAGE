#!/usr/bin/env python3
"""SAGE voice session — push-to-talk voice interface.

Usage:
    python run_sage_voice.py
    python run_sage_voice.py --text   # text-only fallback (no voice hardware)
    python run_sage_voice.py --no-tts # STT in, text out (no speaker)
"""

import os
import sys

from jarvis.config import load_config
from jarvis.identity.loader import IdentityLoader
from jarvis.governance.engine import GovernanceEngine
from jarvis.memory.store import MemoryStore
from jarvis.llm.client import LLMClient
from jarvis.will.loader import WillLoader
from jarvis.core.reasoning_loop import ReasoningLoop

from jarvis.embodiment.stt import STTEngine
from jarvis.embodiment.tts import clean_for_speech, create_tts_engine
from jarvis.embodiment.microphone import record_toggle
from jarvis.embodiment.conversation import VoiceConversation


def _make_embed_fn(config):
    embed_client = LLMClient(
        base_url=config.models.get("ollama_url", "http://localhost:11434"),
        model=config.models.get("embedding", "nomic-embed-text:latest"),
        timeout=config.llm.get("default_timeout", 120),
    )
    return embed_client.embed


def build_sage() -> ReasoningLoop:
    config = load_config("configs/config.yaml")
    ollama_url = config.models.get("ollama_url", "http://localhost:11434")
    model = config.models.get("primary", "llama3.2:latest")
    timeout = config.llm.get("default_timeout", 120)

    identity_loader = IdentityLoader(
        soul_path=config.identity.get("soul_path", "data/soul"),
        constitution_path=config.identity.get("constitution_path", "data/constitution"),
    )
    governance_llm = LLMClient(base_url=ollama_url, model=model, timeout=timeout)
    governance_engine = GovernanceEngine(
        constitution=identity_loader.load_constitution(),
        llm_classify_fn=governance_llm.classify,
    )
    memory_store = MemoryStore(
        chroma_path=config.memory.get("chroma_db_path", "data/chroma_db"),
        embedding_fn=_make_embed_fn(config),
    )
    will_loader = WillLoader("data/will/goals.yaml")
    llm_client = LLMClient(base_url=ollama_url, model=model, timeout=timeout)

    return ReasoningLoop(
        config=config,
        identity_loader=identity_loader,
        governance_engine=governance_engine,
        will_loader=will_loader,
        memory_store=memory_store,
        llm_client=llm_client,
        embed_fn=_make_embed_fn(config),
    )


def voice_mode(no_tts: bool = False) -> None:
    print("SAGE - Voice Session")
    print("Press ENTER to record, press ENTER again to stop.")
    print("Type /help for commands, /quit to exit.")
    print()

    loop = build_sage()
    report = loop._validate_runtime()
    if not report.passed:
        print(f"ERROR: {report.message}")
        sys.exit(1)

    print(f"Runtime: {report.message}")
    stt = STTEngine("tiny")
    tts = None if no_tts else create_tts_engine()
    conv = VoiceConversation(loop=loop, stt_engine=stt, tts_engine=tts, enable_rating=True)

    try:
        while True:
            user_input = input("> ").strip()
            if user_input == "/quit":
                break
            if user_input:
                if user_input.startswith("/"):
                    print(conv.handle_command(user_input))
                else:
                    conv.run_one_text(user_input, speak=True)
                continue

            audio = record_toggle()
            if len(audio) < 8000:
                print("(too short, skipping)")
                continue
            conv.run_one(audio)
    except (EOFError, KeyboardInterrupt):
        print()

    print("Voice session ended.")
    loop.end_session()


def text_mode() -> None:
    print("SAGE - Text Session (no voice)")
    print("Type /help for commands, /quit to exit.")
    print()

    loop = build_sage()
    report = loop._validate_runtime()
    if not report.passed:
        print(f"ERROR: {report.message}")
        sys.exit(1)

    print(f"Runtime: {report.message}")
    stt = STTEngine("tiny")
    conv = VoiceConversation(loop=loop, stt_engine=stt, tts_engine=None, enable_rating=True)

    try:
        while True:
            user_input = input("> ").strip()
            if user_input == "/quit":
                break
            if user_input:
                if user_input.startswith("/"):
                    print(conv.handle_command(user_input))
                else:
                    conv.run_one_text(user_input)
    except (EOFError, KeyboardInterrupt):
        print()

    print("Session ended.")
    loop.end_session()


def main():
    os.makedirs("data", exist_ok=True)

    no_tts = "--no-tts" in sys.argv
    if "--text" in sys.argv:
        text_mode()
    else:
        voice_mode(no_tts=no_tts)


if __name__ == "__main__":
    main()
