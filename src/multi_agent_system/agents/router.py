from __future__ import annotations

from typing import Dict

from ..agent_registry import AgentRegistry
from ..models import RouteDecision, Subtask


class RouterAgent:
    def __init__(self, registry: AgentRegistry, weights: Dict[str, float], min_route_score: float) -> None:
        self.registry = registry
        self.weights = weights
        self.min_route_score = min_route_score

    def route(self, subtask: Subtask) -> RouteDecision:
        best_name = ""
        best_score = -1.0

        for profile in self.registry.list_specialists():
            score = (
                self.weights["capability"] * profile.capability
                + self.weights["confidence"] * profile.confidence_prior
                + self.weights["success_rate"] * profile.success_rate
                - self.weights["cost"] * profile.avg_cost
                - self.weights["latency"] * (profile.avg_latency_ms / 1000.0)
            )
            if score > best_score:
                best_score = score
                best_name = profile.name

        if best_score < self.min_route_score:
            return RouteDecision(
                specialist_name="analysis_specialist",
                route_score=best_score,
                rationale="Fallback route due to low route score",
            )

        return RouteDecision(
            specialist_name=best_name,
            route_score=best_score,
            rationale=f"Best weighted score for subtask: {subtask.id}",
        )
