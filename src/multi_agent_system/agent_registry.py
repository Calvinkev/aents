from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SpecialistProfile:
    name: str
    capabilities: List[str]
    capability: float
    confidence_prior: float
    success_rate: float
    avg_cost: float
    avg_latency_ms: float
    current_workload: int = 0


class AgentRegistry:
    def __init__(self) -> None:
        self._profiles: Dict[str, SpecialistProfile] = {
            "research_specialist": SpecialistProfile(
                name="research_specialist",
                capabilities=["research", "document_analysis", "evidence_summarization", "fact_checking"],
                capability=0.90,
                confidence_prior=0.82,
                success_rate=0.88,
                avg_cost=0.15,
                avg_latency_ms=450,
            ),
            "coding_specialist": SpecialistProfile(
                name="coding_specialist",
                capabilities=["code_analysis", "refactoring", "bug_fix", "patch_application", "test_execution", "coding"],
                capability=0.92,
                confidence_prior=0.85,
                success_rate=0.90,
                avg_cost=0.25,
                avg_latency_ms=650,
            ),
            "debugging_specialist": SpecialistProfile(
                name="debugging_specialist",
                capabilities=["root_cause_analysis", "log_inspection", "reproduction", "fix_verification", "debugging"],
                capability=0.89,
                confidence_prior=0.80,
                success_rate=0.86,
                avg_cost=0.20,
                avg_latency_ms=550,
            ),
            "security_specialist": SpecialistProfile(
                name="security_specialist",
                capabilities=["vulnerability_scan", "auth_audit", "secret_detection", "dependency_audit", "security"],
                capability=0.91,
                confidence_prior=0.84,
                success_rate=0.89,
                avg_cost=0.22,
                avg_latency_ms=500,
            ),
            "data_specialist": SpecialistProfile(
                name="data_specialist",
                capabilities=["data_analysis", "anomaly_detection", "metrics_computation", "statistical_report"],
                capability=0.88,
                confidence_prior=0.81,
                success_rate=0.87,
                avg_cost=0.18,
                avg_latency_ms=480,
            ),
            "general_specialist": SpecialistProfile(
                name="general_specialist",
                capabilities=["general_reasoning", "task_coordination", "summarization"],
                capability=0.80,
                confidence_prior=0.75,
                success_rate=0.83,
                avg_cost=0.10,
                avg_latency_ms=350,
            ),
            "analysis_specialist": SpecialistProfile(
                name="analysis_specialist",
                capabilities=["research", "code_analysis", "general_reasoning"],
                capability=0.86,
                confidence_prior=0.78,
                success_rate=0.85,
                avg_cost=0.18,
                avg_latency_ms=480,
            ),
            "synthesis_specialist": SpecialistProfile(
                name="synthesis_specialist",
                capabilities=["summarization", "task_coordination"],
                capability=0.84,
                confidence_prior=0.77,
                success_rate=0.84,
                avg_cost=0.15,
                avg_latency_ms=400,
            ),
        }

    def list_specialists(self) -> List[SpecialistProfile]:
        return list(self._profiles.values())

    def get(self, name: str) -> Optional[SpecialistProfile]:
        return self._profiles.get(name)

    def update_metrics(self, name: str, success: bool, latency_ms: int = 0, cost: float = 0.0) -> None:
        profile = self._profiles.get(name)
        if not profile:
            return
        delta = 0.02 if success else -0.05
        profile.success_rate = min(0.99, max(0.1, profile.success_rate + delta))
        if latency_ms > 0:
            profile.avg_latency_ms = (profile.avg_latency_ms * 0.8) + (latency_ms * 0.2)
        if cost > 0:
            profile.avg_cost = (profile.avg_cost * 0.8) + (cost * 0.2)

    def update_success(self, name: str, success: bool) -> None:
        self.update_metrics(name, success)
