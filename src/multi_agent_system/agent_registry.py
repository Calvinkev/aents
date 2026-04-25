from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SpecialistProfile:
    name: str
    capability: float
    confidence_prior: float
    success_rate: float
    avg_cost: float
    avg_latency_ms: float


class AgentRegistry:
    def __init__(self) -> None:
        self._profiles: Dict[str, SpecialistProfile] = {
            "analysis_specialist": SpecialistProfile(
                name="analysis_specialist",
                capability=0.86,
                confidence_prior=0.78,
                success_rate=0.82,
                avg_cost=0.25,
                avg_latency_ms=520,
            ),
            "research_specialist": SpecialistProfile(
                name="research_specialist",
                capability=0.8,
                confidence_prior=0.74,
                success_rate=0.79,
                avg_cost=0.2,
                avg_latency_ms=600,
            ),
            "synthesis_specialist": SpecialistProfile(
                name="synthesis_specialist",
                capability=0.84,
                confidence_prior=0.77,
                success_rate=0.81,
                avg_cost=0.23,
                avg_latency_ms=560,
            ),
        }

    def list_specialists(self) -> List[SpecialistProfile]:
        return list(self._profiles.values())

    def get(self, name: str) -> SpecialistProfile:
        return self._profiles[name]

    def update_success(self, name: str, success: bool) -> None:
        profile = self._profiles[name]
        delta = 0.02 if success else -0.03
        profile.success_rate = min(0.99, max(0.01, profile.success_rate + delta))
