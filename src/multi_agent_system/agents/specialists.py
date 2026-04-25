from __future__ import annotations

from typing import Protocol

from ..models import CandidateResult, Subtask


class Specialist(Protocol):
    def execute(self, subtask: Subtask, guidance: str = "") -> CandidateResult:
        ...


class AnalysisSpecialist:
    name = "analysis_specialist"

    def execute(self, subtask: Subtask, guidance: str = "") -> CandidateResult:
        confidence = 0.72 if "tighten" in guidance.lower() else 0.78
        criteria_text = ", ".join(subtask.acceptance_criteria)
        return CandidateResult(
            subtask_id=subtask.id,
            content=(
                f"[Analysis] Objective handled: {subtask.objective}. "
                f"Criteria addressed: {criteria_text}. "
                f"Guidance: {guidance or 'none'}."
            ),
            evidence=["context extraction", "structured constraints"],
            confidence=confidence,
            estimated_cost=0.2,
            estimated_latency_ms=450,
        )


class ResearchSpecialist:
    name = "research_specialist"

    def execute(self, subtask: Subtask, guidance: str = "") -> CandidateResult:
        confidence = 0.7 if "strict" in guidance.lower() else 0.75
        criteria_text = ", ".join(subtask.acceptance_criteria)
        return CandidateResult(
            subtask_id=subtask.id,
            content=(
                f"[Research] Findings compiled for {subtask.title}. "
                f"Criteria addressed: {criteria_text}. "
                f"Guidance: {guidance or 'none'}."
            ),
            evidence=["evidence set A", "evidence set B"],
            confidence=confidence,
            estimated_cost=0.18,
            estimated_latency_ms=610,
        )


class SynthesisSpecialist:
    name = "synthesis_specialist"

    def execute(self, subtask: Subtask, guidance: str = "") -> CandidateResult:
        confidence = 0.8 if "refine" in guidance.lower() else 0.77
        criteria_text = ", ".join(subtask.acceptance_criteria)
        return CandidateResult(
            subtask_id=subtask.id,
            content=(
                f"[Synthesis] Consolidated output for {subtask.title}. "
                f"Criteria addressed: {criteria_text}. "
                f"Guidance: {guidance or 'none'}."
            ),
            evidence=["merged narrative", "consistency checks"],
            confidence=confidence,
            estimated_cost=0.24,
            estimated_latency_ms=530,
        )
