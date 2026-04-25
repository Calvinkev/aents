from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

from .agent_registry import AgentRegistry
from .agents.failure_handler import FailureHandler
from .agents.memory import MemoryLearningAgent
from .agents.optimizer import OptimizerAgent
from .agents.planner import PlannerAgent
from .agents.refiner import CriticRefinerAgent
from .agents.router import RouterAgent
from .agents.specialists import AnalysisSpecialist, ResearchSpecialist, SynthesisSpecialist
from .agents.validator import ValidatorAgent
from .models import CandidateResult, TaskState, ValidationStatus


class EscalationAgent:
    def escalate(self, task: str, reason: str, traces: List[Dict[str, object]]) -> str:
        return (
            f"ESCALATED TASK: {task}\n"
            f"REASON: {reason}\n"
            f"TRACE_ENTRIES: {len(traces)}\n"
            "ACTION: Human review required with attached trace context."
        )


class Orchestrator:
    def __init__(self, config: Dict[str, object]) -> None:
        system = config["system"]
        routing = config["routing"]
        failure_policy = config["failure_policy"]

        self.max_iterations = int(system["max_iterations"])
        self.max_retries_per_subtask = int(system["max_retries_per_subtask"])
        self.optimization_enabled = bool(system["optimization_enabled"])

        self.registry = AgentRegistry()
        self.planner = PlannerAgent()
        self.router = RouterAgent(
            registry=self.registry,
            weights=dict(routing["weights"]),
            min_route_score=float(system["min_route_score"]),
        )
        self.validator = ValidatorAgent(quality_threshold=float(system["quality_threshold"]))
        self.refiner = CriticRefinerAgent()
        self.optimizer = OptimizerAgent()
        self.failure_handler = FailureHandler(
            retry_backoff_seconds=list(failure_policy["retry_backoff_seconds"]),
            failure_threshold=int(failure_policy["circuit_breaker_failure_threshold"]),
            use_fallback_specialist=bool(failure_policy["use_fallback_specialist"]),
        )
        self.memory = MemoryLearningAgent()
        self.escalation = EscalationAgent()

        self.specialists = {
            "analysis_specialist": AnalysisSpecialist(),
            "research_specialist": ResearchSpecialist(),
            "synthesis_specialist": SynthesisSpecialist(),
        }

    def run(self, task: str) -> TaskState:
        state = TaskState(task=task)
        subtasks = self.planner.plan(task)

        final_chunks: List[str] = []

        for subtask in subtasks:
            guidance = ""
            retry = 0
            completed_subtask = False

            while retry <= self.max_retries_per_subtask:
                state.iteration += 1
                if state.iteration > self.max_iterations:
                    state.escalated = True
                    state.final_output = self.escalation.escalate(
                        task=task,
                        reason="Max iteration budget exceeded",
                        traces=state.traces,
                    )
                    return state

                route = self.router.route(subtask)
                specialist_name = route.specialist_name
                specialist = self.specialists[specialist_name]

                candidate: CandidateResult = specialist.execute(subtask, guidance=guidance)
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
                self.registry.update_success(specialist_name, success=success)
                self.memory.record(
                    specialist_name=specialist_name,
                    success=success,
                    score=route.route_score,
                    cost=candidate.estimated_cost,
                    latency_ms=candidate.estimated_latency_ms,
                )

                if validation.status == ValidationStatus.PASS:
                    accepted = self.optimizer.optimize(candidate) if self.optimization_enabled else candidate
                    final_chunks.append(accepted.content)
                    completed_subtask = True
                    break

                self.failure_handler.record_failure(specialist_name)
                decision = self.failure_handler.decide(
                    specialist_name=specialist_name,
                    retry_index=retry,
                    max_retries=self.max_retries_per_subtask,
                )

                if validation.status == ValidationStatus.SOFT_FAIL and decision.should_retry:
                    guidance = self.refiner.refine_guidance(guidance, validation)
                    self.failure_handler.apply_backoff(decision.backoff_seconds)
                    retry += 1
                    continue

                if validation.status == ValidationStatus.HARD_FAIL and decision.should_retry:
                    if decision.use_fallback_specialist:
                        guidance = "Fallback route required due to stability issues"
                    else:
                        guidance = self.refiner.refine_guidance(guidance, validation)
                    self.failure_handler.apply_backoff(decision.backoff_seconds)
                    retry += 1
                    continue

                if decision.should_escalate:
                    state.escalated = True
                    state.final_output = self.escalation.escalate(
                        task=task,
                        reason=(
                            f"Subtask {subtask.id} failed after retries. "
                            f"Last status: {validation.status.value}"
                        ),
                        traces=state.traces,
                    )
                    return state

            if not completed_subtask:
                state.escalated = True
                state.final_output = self.escalation.escalate(
                    task=task,
                    reason=f"Subtask {subtask.id} incomplete without valid output",
                    traces=state.traces,
                )
                return state

        memory_summary = self.memory.summary()
        state.completed = True
        state.final_output = (
            "\n".join(final_chunks)
            + "\n\n"
            + f"Execution metrics: {memory_summary}"
        )
        return state
