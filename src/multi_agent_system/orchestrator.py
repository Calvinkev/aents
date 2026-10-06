from __future__ import annotations

import asyncio
from dataclasses import asdict
import logging
import time
from typing import Any, Callable, Dict, List, Optional
import uuid

from .agent_registry import AgentRegistry
from .agents.base import AgentResult, BaseAgent
from .agents.failure_handler import FailureHandler
from .agents.memory import MemoryLearningAgent
from .agents.optimizer import OptimizerAgent
from .agents.planner import PlannerAgent
from .agents.refiner import CriticRefinerAgent
from .agents.router import RouterAgent
from .agents.specialists import (
    CodingAgent,
    DataAgent,
    DebuggingAgent,
    GeneralAgent,
    LegacySpecialistAdapter,
    ResearchAgent,
    SecurityAgent,
)
from .agents.validator import ValidatorAgent
from .models import CandidateResult, Subtask, TaskState, ValidationStatus
from .tools.filesystem import register_filesystem_tools
from .tools.git_github import register_git_github_tools
from .tools.http_db import register_http_db_tools
from .tools.registry import ToolRegistry
from .tools.shell import register_shell_tools

logger = logging.getLogger(__name__)


class EscalationAgent:
    def escalate(self, task: str, reason: str, traces: List[Dict[str, object]]) -> str:
        return (
            f"ESCALATED TASK: {task}\n"
            f"REASON: {reason}\n"
            f"TRACE_ENTRIES: {len(traces)}\n"
            "ACTION: Human review required with attached trace context."
        )


class Orchestrator:
    """Production Multi-Agent Orchestrator managing DAG execution, parallel agents, budgets, and traceability."""

    def __init__(
        self,
        config: Dict[str, object],
        event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        system = config.get("system", {})
        routing = config.get("routing", {})
        failure_policy = config.get("failure_policy", {})
        budgets = config.get("budgets", {})

        self.max_iterations = int(system.get("max_iterations", 8))
        self.max_retries_per_subtask = int(system.get("max_retries_per_subtask", 3))
        self.optimization_enabled = bool(system.get("optimization_enabled", True))

        self.max_task_cost = float(budgets.get("max_task_cost", 5.0))
        self.max_tokens = int(budgets.get("max_tokens", 100000))
        self.max_execution_time = float(budgets.get("max_execution_time_seconds", 300))

        self.event_callback = event_callback

        self.registry = AgentRegistry()
        self.tool_registry = ToolRegistry()
        register_filesystem_tools(self.tool_registry)
        register_shell_tools(self.tool_registry)
        register_git_github_tools(self.tool_registry)
        register_http_db_tools(self.tool_registry)

        self.planner = PlannerAgent()
        self.router = RouterAgent(
            registry=self.registry,
            weights=dict(routing.get("weights", {
                "capability": 0.35,
                "confidence": 0.2,
                "success_rate": 0.25,
                "cost": 0.1,
                "latency": 0.1,
            })),
            min_route_score=float(system.get("min_route_score", 0.45)),
        )
        self.validator = ValidatorAgent(quality_threshold=float(system.get("quality_threshold", 0.65)))
        self.refiner = CriticRefinerAgent()
        self.optimizer = OptimizerAgent()
        self.failure_handler = FailureHandler(
            retry_backoff_seconds=list(failure_policy.get("retry_backoff_seconds", [0.2, 0.5, 1.0])),
            failure_threshold=int(failure_policy.get("circuit_breaker_failure_threshold", 5)),
            use_fallback_specialist=bool(failure_policy.get("use_fallback_specialist", True)),
        )
        self.memory = MemoryLearningAgent()
        self.escalation = EscalationAgent()

        self.real_agents: Dict[str, BaseAgent] = {
            "research_specialist": ResearchAgent(tool_registry=self.tool_registry),
            "coding_specialist": CodingAgent(tool_registry=self.tool_registry),
            "debugging_specialist": DebuggingAgent(tool_registry=self.tool_registry),
            "security_specialist": SecurityAgent(tool_registry=self.tool_registry),
            "data_specialist": DataAgent(tool_registry=self.tool_registry),
            "general_specialist": GeneralAgent(tool_registry=self.tool_registry),
            "analysis_specialist": ResearchAgent(tool_registry=self.tool_registry),
            "synthesis_specialist": GeneralAgent(tool_registry=self.tool_registry),
        }

        # Legacy adapters for compatibility
        self.specialists = {
            k: LegacySpecialistAdapter(v) for k, v in self.real_agents.items()
        }

    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        if self.event_callback:
            try:
                self.event_callback(event_type, data)
            except Exception as e:
                logger.warning(f"Error in event callback: {e}")

    async def run_async(self, task: str, task_id: Optional[str] = None) -> TaskState:
        """Asynchronously execute task DAG with parallel worker coordination and budget enforcement."""
        task_id = task_id or str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        state = TaskState(task=task, task_id=task_id, run_id=run_id)

        start_time = time.time()
        total_task_cost = 0.0
        total_task_tokens = 0

        self._emit_event("TASK_STARTED", {"task_id": task_id, "run_id": run_id, "task": task})

        subtasks = await self.planner.plan_dag(task)
        self._emit_event("PLAN_CREATED", {"task_id": task_id, "subtasks": [asdict(st) for st in subtasks]})

        completed_subtasks: Dict[str, CandidateResult] = {}
        pending_subtasks: Dict[str, Subtask] = {st.id: st for st in subtasks}

        while pending_subtasks:
            elapsed_time = time.time() - start_time
            if elapsed_time > self.max_execution_time or total_task_cost > self.max_task_cost or total_task_tokens > self.max_tokens:
                state.escalated = True
                reason = f"Budget/Timeout Exceeded: Elapsed {elapsed_time:.1f}s, Cost ${total_task_cost:.2f}, Tokens {total_task_tokens}"
                self._emit_event("TASK_FAILED", {"task_id": task_id, "reason": reason})
                state.final_output = self.escalation.escalate(task=task, reason=reason, traces=state.traces)
                return state

            ready_subtasks: List[Subtask] = []
            for st_id, st in list(pending_subtasks.items()):
                deps_met = all(dep in completed_subtasks for dep in st.dependencies)
                if deps_met:
                    ready_subtasks.append(st)

            if not ready_subtasks:
                state.escalated = True
                state.final_output = self.escalation.escalate(
                    task=task,
                    reason="Dependency deadlock or unsatisfied subtask dependency in DAG",
                    traces=state.traces,
                )
                return state

            tasks = [
                self._execute_subtask(st, state, task_id, run_id)
                for st in ready_subtasks
            ]

            results = await asyncio.gather(*tasks)

            for st, candidate_res, success in results:
                if success and candidate_res:
                    completed_subtasks[st.id] = candidate_res
                    del pending_subtasks[st.id]
                    total_task_cost += candidate_res.estimated_cost
                    total_task_tokens += candidate_res.metadata.get("tokens_used", 100)
                else:
                    state.escalated = True
                    state.final_output = self.escalation.escalate(
                        task=task,
                        reason=f"Subtask {st.id} failed validation after retries.",
                        traces=state.traces,
                    )
                    return state

        final_chunks = [cand.content for cand in completed_subtasks.values()]
        memory_summary = self.memory.summary()

        state.completed = True
        state.final_output = (
            "\n".join(final_chunks)
            + "\n\n"
            + f"Execution metrics: {memory_summary}"
        )

        self._emit_event("TASK_COMPLETED", {"task_id": task_id, "final_output": state.final_output})
        return state

    async def _execute_subtask(
        self,
        subtask: Subtask,
        state: TaskState,
        task_id: str,
        run_id: str,
    ) -> tuple[Subtask, Optional[CandidateResult], bool]:
        guidance = ""
        retry = 0

        while retry <= self.max_retries_per_subtask:
            state.iteration += 1
            if state.iteration > self.max_iterations:
                return subtask, None, False

            route = self.router.route(subtask)
            specialist_name = route.specialist_name
            real_agent = self.real_agents.get(specialist_name, self.real_agents["general_specialist"])

            self._emit_event("AGENT_SELECTED", {
                "subtask_id": subtask.id,
                "agent_id": specialist_name,
                "route_score": route.route_score,
            })

            agent_res: AgentResult = await real_agent.run(
                task_id=task_id,
                subtask_id=subtask.id,
                task_description=subtask.objective,
                guidance=guidance,
            )

            candidate = CandidateResult(
                subtask_id=subtask.id,
                content=agent_res.output,
                evidence=agent_res.evidence,
                confidence=agent_res.confidence,
                estimated_cost=agent_res.estimated_cost,
                estimated_latency_ms=agent_res.latency_ms,
                metadata={
                    "agent_id": agent_res.agent_id,
                    "tokens_used": agent_res.tokens_used,
                    "tool_calls": agent_res.tool_calls,
                },
            )

            validation = self.validator.validate(subtask, candidate)

            trace_entry: Dict[str, object] = {
                "subtask_id": subtask.id,
                "route": asdict(route),
                "candidate": asdict(candidate),
                "validation": asdict(validation),
                "retry": retry,
            }
            state.traces.append(trace_entry)

            success = validation.status == ValidationStatus.PASS
            self.registry.update_metrics(
                name=specialist_name,
                success=success,
                latency_ms=agent_res.latency_ms,
                cost=agent_res.estimated_cost,
            )
            self.memory.record(
                specialist_name=specialist_name,
                success=success,
                score=route.route_score,
                cost=candidate.estimated_cost,
                latency_ms=candidate.estimated_latency_ms,
            )

            if success:
                accepted = self.optimizer.optimize(candidate) if self.optimization_enabled else candidate
                self._emit_event("VALIDATION_PASSED", {"subtask_id": subtask.id, "score": validation.score})
                return subtask, accepted, True

            self._emit_event("VALIDATION_FAILED", {
                "subtask_id": subtask.id,
                "status": validation.status.value,
                "reasons": validation.reasons,
            })

            self.failure_handler.record_failure(specialist_name)
            decision = self.failure_handler.decide(
                specialist_name=specialist_name,
                retry_index=retry,
                max_retries=self.max_retries_per_subtask,
            )

            if decision.should_retry:
                guidance = self.refiner.refine_guidance(guidance, validation)
                if decision.backoff_seconds > 0:
                    await asyncio.sleep(decision.backoff_seconds)
                retry += 1
                continue

            return subtask, candidate, False

        return subtask, None, False

    def run(self, task: str) -> TaskState:
        try:
            return asyncio.run(self.run_async(task))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.run_async(task))
