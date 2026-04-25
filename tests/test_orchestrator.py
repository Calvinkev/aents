from src.multi_agent_system.orchestrator import Orchestrator


BASE_CONFIG = {
    "system": {
        "max_iterations": 20,
        "max_retries_per_subtask": 3,
        "min_route_score": 0.1,
        "quality_threshold": 0.65,
        "optimization_enabled": True,
        "allow_parallel_candidates": True,
    },
    "routing": {
        "weights": {
            "capability": 0.35,
            "confidence": 0.2,
            "success_rate": 0.25,
            "cost": 0.1,
            "latency": 0.1,
        }
    },
    "failure_policy": {
        "retry_backoff_seconds": [0.0, 0.0, 0.0],
        "use_fallback_specialist": True,
        "circuit_breaker_failure_threshold": 5,
        "escalate_on_budget_exhaustion": True,
    },
    "scalability": {
        "queue_name": "task-dispatch",
        "worker_pool_min": 2,
        "worker_pool_max": 16,
        "autoscale_target_queue_depth": 25,
        "enable_trace_sampling": True,
    },
}


def test_orchestrator_completes_happy_path() -> None:
    orchestrator = Orchestrator(config=BASE_CONFIG)
    state = orchestrator.run("Draft an implementation strategy for migration")

    assert state.completed is True
    assert state.escalated is False
    assert state.final_output is not None
    assert "Execution metrics" in state.final_output
    assert len(state.traces) >= 3


def test_orchestrator_escalates_when_iterations_too_low() -> None:
    config = {
        **BASE_CONFIG,
        "system": {
            **BASE_CONFIG["system"],
            "max_iterations": 1,
            "quality_threshold": 0.95,
        },
    }
    orchestrator = Orchestrator(config=config)
    state = orchestrator.run("Complex task likely needing retries")

    assert state.completed is False
    assert state.escalated is True
    assert state.final_output is not None
    assert "ESCALATED TASK" in state.final_output
