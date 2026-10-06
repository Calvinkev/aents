from __future__ import annotations

import logging
from typing import List, Optional

from ..models import CandidateResult, Subtask, ValidationReport, ValidationStatus

logger = logging.getLogger(__name__)


class ValidatorAgent:
    """Multi-aspect Validator that evaluates output structure, rules, evidence, and criteria."""

    def __init__(self, quality_threshold: float = 0.65):
        self.quality_threshold = quality_threshold

    def validate(self, subtask: Subtask, candidate: CandidateResult) -> ValidationReport:
        hard_fail_reasons: List[str] = []
        soft_fail_reasons: List[str] = []

        # 1. Structural Check
        if not candidate.content or not candidate.content.strip():
            hard_fail_reasons.append("Empty output received from agent.")

        # 2. Evidence Check
        if not candidate.evidence:
            soft_fail_reasons.append("No supporting evidence or tool output attached.")

        # Calculate score from candidate confidence and evidence count
        evidence_bonus = min(0.15, len(candidate.evidence or []) * 0.05)
        score = min(1.0, candidate.confidence + evidence_bonus)

        # 3. Acceptance Criteria Check
        if subtask.acceptance_criteria:
            missing_criteria = []
            content_lower = candidate.content.lower()
            for criterion in subtask.acceptance_criteria:
                words = [w.lower() for w in criterion.split() if len(w) > 4]
                if words and not any(w in content_lower for w in words):
                    missing_criteria.append(criterion)

            if len(missing_criteria) == len(subtask.acceptance_criteria) and len(subtask.acceptance_criteria) > 1:
                soft_fail_reasons.append(f"Missing criteria signals: {missing_criteria[:2]}")

        # Return HARD_FAIL if structural or severe errors exist
        if hard_fail_reasons:
            return ValidationReport(
                status=ValidationStatus.HARD_FAIL,
                score=score,
                reasons=hard_fail_reasons,
                suggested_fixes=["Regenerate output with valid structure and content."],
            )

        # Return SOFT_FAIL if score below threshold or critical soft fail reasons
        if score < self.quality_threshold or (len(soft_fail_reasons) > 1 and score < 0.85):
            return ValidationReport(
                status=ValidationStatus.SOFT_FAIL,
                score=score,
                reasons=soft_fail_reasons or ["Quality score below required threshold"],
                suggested_fixes=[
                    "Provide explicit evidence from tool calls.",
                    "Ensure response explicitly addresses acceptance criteria.",
                ],
            )

        return ValidationReport(
            status=ValidationStatus.PASS,
            score=max(score, self.quality_threshold),
            reasons=["All validation checks passed successfully."],
            suggested_fixes=[],
        )
