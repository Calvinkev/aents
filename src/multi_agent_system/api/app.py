from __future__ import annotations

import asyncio
import datetime
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from ..agent_registry import AgentRegistry
from ..config_loader import load_config
from ..db.session import init_db
from ..orchestrator import Orchestrator
from ..tools.approval import global_approval_manager
from ..tools.registry import ToolRegistry
from .events import router as events_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AENTS - Production AI Agent Platform API",
    version="1.0.0",
    description="REST API for multi-agent orchestration, task tracking, tool permissions, and real-time observability.",
)

app.include_router(events_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks_db: Dict[str, Dict[str, Any]] = {}
runs_db: Dict[str, Dict[str, Any]] = {}

config_path = os.getenv("CONFIG_PATH", "config/system_config.yaml")
try:
    config = load_config(config_path)
except Exception:
    config = {
        "system": {"max_iterations": 8, "min_route_score": 0.45, "quality_threshold": 0.75},
        "routing": {"weights": {"capability": 0.35, "confidence": 0.2, "success_rate": 0.25, "cost": 0.1, "latency": 0.1}},
        "failure_policy": {"retry_backoff_seconds": [0.2, 0.5, 1.0], "use_fallback_specialist": True, "circuit_breaker_failure_threshold": 5},
        "budgets": {"max_task_cost": 5.0, "max_tokens": 100000, "max_execution_time_seconds": 300},
    }

registry = AgentRegistry()


@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database init deferred: {e}")


class CreateTaskRequest(BaseModel):
    task: str
    project_id: Optional[str] = None
    priority: int = 1


class TaskResponse(BaseModel):
    task_id: str
    task: str
    status: str
    created_at: str
    completed: bool = False
    escalated: bool = False
    final_output: Optional[str] = None


class ApprovalDecisionRequest(BaseModel):
    decided_by: str = "admin"


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now(datetime.UTC).isoformat(), "database": "online", "llm_provider": os.getenv("LLM_PROVIDER", "openai")}


@app.get("/ready")
async def ready_check():
    return {"status": "ready"}


@app.get("/metrics")
async def metrics_endpoint():
    total_tasks = len(tasks_db)
    completed = sum(1 for t in tasks_db.values() if t.get("status") == "completed")
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed,
        "failed_tasks": sum(1 for t in tasks_db.values() if t.get("status") == "failed"),
        "success_rate": (completed / total_tasks) if total_tasks > 0 else 1.0,
        "active_agents": len(registry.list_specialists()),
    }


@app.post("/api/v1/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(req: CreateTaskRequest, background_tasks: BackgroundTasks):
    import uuid
    task_id = str(uuid.uuid4())
    task_data = {
        "task_id": task_id,
        "task": req.task,
        "status": "queued",
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "completed": False,
        "escalated": False,
        "final_output": None,
        "traces": [],
    }
    tasks_db[task_id] = task_data

    def run_task_in_bg(t_id: str, t_str: str):
        orc = Orchestrator(config=config)
        task_data["status"] = "running"
        state = orc.run(t_str)
        task_data["completed"] = state.completed
        task_data["escalated"] = state.escalated
        task_data["status"] = "completed" if state.completed else ("escalated" if state.escalated else "failed")
        task_data["final_output"] = state.final_output
        task_data["traces"] = state.traces

    background_tasks.add_task(run_task_in_bg, task_id, req.task)
    return TaskResponse(**task_data)


@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**tasks_db[task_id])


@app.get("/api/v1/agents")
async def list_agents():
    agents = []
    for profile in registry.list_specialists():
        agents.append({
            "agent_id": profile.name,
            "name": profile.name,
            "capabilities": profile.capabilities,
            "success_rate": profile.success_rate,
            "avg_latency_ms": profile.avg_latency_ms,
            "avg_cost": profile.avg_cost,
        })
    return {"agents": agents}


@app.get('/', response_class=HTMLResponse)
@app.get('/dashboard', response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_path = os.path.join(os.path.dirname(__file__), '../dashboard/index.html')
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r') as f:
            return f.read()
    return '<h1>AENTS Control Center</h1>'
