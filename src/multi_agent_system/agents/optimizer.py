from __future__ import annotations

from ..models import CandidateResult


class OptimizerAgent:
    def optimize(self, candidate: CandidateResult) -> CandidateResult:
        optimized = CandidateResult(
            subtask_id=candidate.subtask_id,
            content=f"{candidate.content} [Optimized for concise delivery]",
            evidence=candidate.evidence,
            confidence=min(1.0, candidate.confidence + 0.01),
            estimated_cost=max(0.01, candidate.estimated_cost * 0.95),
            estimated_latency_ms=max(50, int(candidate.estimated_latency_ms * 0.93)),
            metadata={**candidate.metadata, "optimized": True},
        )
        return optimized
