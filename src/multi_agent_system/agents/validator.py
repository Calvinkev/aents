from __future__ import annotations

from ..models import CandidateResult, Subtask, ValidationReport, ValidationStatus


class ValidatorAgent:
    def __init__(self, quality_threshold: float) -> None:
        self.quality_threshold = quality_threshold

    def validate(self, subtask: Subtask, candidate: CandidateResult) -> ValidationReport:
        hard_fail_reasons = []
        soft_fail_reasons = []

        if not candidate.content.strip():
            hard_fail_reasons.append("Empty output")

        if len(candidate.evidence) == 0:
            hard_fail_reasons.append("No evidence provided")

        score = min(1.0, candidate.confidence + (0.05 * min(len(candidate.evidence), 3)))

        for criterion in subtask.acceptance_criteria:
            key = criterion.split()[0].lower()
            if key not in candidate.content.lower():
                soft_fail_reasons.append(f"Potentially missing criterion signal: {criterion}")

        if hard_fail_reasons:
            return ValidationReport(
                status=ValidationStatus.HARD_FAIL,
                score=score,
                reasons=hard_fail_reasons,
                suggested_fixes=["Regenerate with mandatory structure and evidence"],
            )

        if score < self.quality_threshold or soft_fail_reasons:
            return ValidationReport(
                status=ValidationStatus.SOFT_FAIL,
                score=score,
                reasons=soft_fail_reasons or ["Quality score below threshold"],
                suggested_fixes=[
                    "Tighten structure to explicitly address criteria",
                    "Increase confidence with more precise evidence",
                ],
            )

        return ValidationReport(
            status=ValidationStatus.PASS,
            score=score,
            reasons=["All checks passed"],
            suggested_fixes=[],
        )
