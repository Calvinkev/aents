from __future__ import annotations

from ..models import ValidationReport


class CriticRefinerAgent:
    def refine_guidance(self, previous_guidance: str, report: ValidationReport) -> str:
        fixes = " | ".join(report.suggested_fixes)
        base = previous_guidance.strip()
        if base:
            return f"{base} | Refine: {fixes}"
        return f"Refine: {fixes}"
