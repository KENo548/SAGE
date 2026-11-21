# SAGE

**A local, voice-activated AI agent with persistent memory.** SAGE is the pilot for JARVIS, a longer-term project exploring portable agentic AI with efficient orchestration and human oversight.

**Status: pilot.** The core agent runs; the orchestration layer described under [Roadmap](#roadmap) is planned, not built.

## What it does today

- Runs locally, with a text entry point and a voice entry point
- Keeps persistent memory, including a constitution-style set of standing instructions the agent reads every session
- Runs an agentic workflow on top of that memory

<!-- TODO: add one concrete example, e.g. "Ask SAGE X -> it does Y". A short demo GIF or transcript is the single most useful addition here. -->

## Run it

```bash
# Text mode
python run_sage.py

# Voice mode
python run_sage_voice.py
```

<!-- TODO: Python version, `pip install -r requirements.txt` (or equivalent), required models/API keys and where to put them -->

## Repository layout

| Path | Contents |
| --- | --- |
| `run_sage.py`, `run_sage_voice.py` | Entry points |
| `jarvis/` | Agent code |
| `configs/` | Configuration |
| `data/` | Local data and memory |
| `labs/` | Experiments |
| `scripts/` | Helper scripts |
| `tests/` | Tests |
| `PLANS/`, `REPORTS/` | Planning notes and benchmark reports |
| `.github/workflows/` | CI |

<!-- TODO: check each description against the actual folder contents -->

## Design principles

- **Local first:** runs on modest hardware (developed on 8 GB RAM and a GTX 1650).
- **Few active agents, many available capabilities:** extra reasoning agents add cost, latency and coordination overhead, so capabilities are loaded as needed.
- **Evidence before adoption:** tools are benchmarked before being adopted, and failed runs are recorded instead of hidden.
- **Human approval for consequential actions.**

<!-- TODO: confirm these match your JARVIS doctrine docs -->

## Roadmap

- [ ] Orchestrator that can recruit sub-agents from public Git repositories
- [ ] Evaluation harness for comparing agents and tools
- [ ] Portability: run the same agent across machines

<!-- TODO: edit to match your real plan -->

## Limitations

- Pilot-stage software; interfaces will change.
- Local models are limited by available hardware, and provider outages can affect any hosted components.
