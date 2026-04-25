# Multi-Agent AI System for [task]

This repository provides a runnable, production-style multi-agent workflow for any `[task]`.

It includes:
- Clear flow chart and architecture documentation
- Agent role definitions (inputs, outputs, decision logic)
- Task routing and confidence-based execution
- Validation + refinement loops until completion
- Failure handling (retry, backoff, dead-letter style capture, escalation)
- Optimization hooks (cost/latency/quality trade-offs)
- Scalability-ready configuration and worker model

## Quick Start

## 1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Run the system

```bash
python -m src.multi_agent_system.main --task "Analyze quarterly support tickets and produce root-cause report"
```

### Run with your own task and actually see output

Use any task string you want:

```bash
python -m src.multi_agent_system.main --task "YOUR TASK HERE"
```

Show full execution details (routing, validation, retries, decisions):

```bash
python -m src.multi_agent_system.main --task "YOUR TASK HERE" --show-trace
```

Save output to a file so you can inspect it later:

```bash
python -m src.multi_agent_system.main --task "YOUR TASK HERE" --show-trace | tee run_output.txt
```

In the output, check these sections:
- `=== FINAL OUTPUT ===` final assembled response
- `=== STATUS ===` completion vs escalation and iteration count
- `=== TRACE ===` step-by-step task routing and validation results

## 3) Run tests

```bash
pytest -q
```

## Project Structure

- `src/multi_agent_system/` core runtime
- `config/system_config.yaml` runtime config, thresholds, retry policy
- `docs/architecture.md` design details and flow chart
- `tests/` validation of orchestration behavior

## Notes

- Replace `[task]` at runtime via CLI argument.
- The example specialists are deterministic simulation agents to demonstrate control flow.
- Integrate real LLM/tool calls by replacing `execute()` methods in specialist agents.
