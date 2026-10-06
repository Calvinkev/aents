# AENTS — Production AI Agent Orchestration Platform

AENTS is a functional, production-oriented AI-agent orchestration platform. It converts high-level autonomous tasks into structured execution plans (DAGs), routes work to real LLM-powered specialist agents, executes sandboxed tools, validates results, recovers from failures, and persists complete execution traces.

---

## Key Features

- **LLM Abstraction**: Configurable OpenAI & OpenAI-compatible providers (`gpt-4o`, `gpt-4o-mini`, local models) with token and cost tracking.
- **Real Specialist Agents**: Research, Coding, Debugging, Security, Data, and General agents executing multi-turn tool loops.
- **Sandboxed Tool System**: Filesystem (with path traversal security bounds), Shell (command policies), Git, GitHub, HTTP (SSRF protected), and Database query tools.
- **Human-in-the-Loop (HITL)**: Approval state machine for sensitive write operations.
- **LLM Planner & Dynamic Router**: Converts tasks into DAGs and routes subtasks based on weighted capability, success rate, latency, cost, and workload metrics.
- **Multi-Aspect Validation & Refinement**: Automatic structural, rule, and evidence validation with soft-fail prompt refinement loops and hard-fail circuit breakers.
- **FastAPI REST API & SSE Events**: Production API with real-time Server-Sent Events (SSE) and worker queue dispatch.
- **Web Dashboard Control Center**: Real-time monitoring UI at `/dashboard`.

---

## Quick Start

### 1) Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configuration

Copy `.env.example` to `.env` and set your API keys:

```bash
cp .env.example .env
```

### 3) CLI Execution

Run an autonomous task with CLI:

```bash
python -m src.multi_agent_system.main run "Analyze repository and identify security issues" --show-trace
```

Output as machine-readable JSON:

```bash
python -m src.multi_agent_system.main run "Analyze quarterly support tickets" --json
```

List registered agents and tools:

```bash
python -m src.multi_agent_system.main agents
python -m src.multi_agent_system.main tools
```

### 4) Run REST API Server & Control Center Dashboard

```bash
uvicorn src.multi_agent_system.api.app:app --host 0.0.0.0 --port 8000
```

Open Dashboard in browser: `http://localhost:8000/dashboard`

---

## Docker Deployment

Launch full stack with API, Worker Queue, and Redis:

```bash
docker-compose up -d --build
```

---

## Running Tests

Run complete test suite:

```bash
pytest tests/ -v
```

---

## Documentation

Detailed documentation is available in `docs/`:
- `docs/architecture.md`
- `docs/agents.md`
- `docs/tools.md`
- `docs/security.md`
- `docs/api.md`
- `docs/deployment.md`
- `docs/observability.md`
- `docs/memory.md`
- `docs/development.md`
