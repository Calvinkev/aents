from __future__ import annotations

from typing import List

from ..models import Subtask


class PlannerAgent:
    def plan(self, task: str) -> List[Subtask]:
        return [
            Subtask(
                id="s1",
                title="Understand Task",
                objective=f"Extract key intent and constraints from: {task}",
                acceptance_criteria=[
                    "Intent is explicit",
                    "Constraints are listed",
                    "Assumptions are documented",
                ],
                priority=1,
            ),
            Subtask(
                id="s2",
                title="Generate Solution",
                objective="Produce the core deliverable for the requested task",
                acceptance_criteria=[
                    "Output addresses the objective",
                    "Reasoning is coherent",
                    "Format is usable",
                ],
                priority=2,
            ),
            Subtask(
                id="s3",
                title="Finalize Response",
                objective="Refine, summarize, and package final output",
                acceptance_criteria=[
                    "Output is clear",
                    "Actionable next steps included",
                ],
                priority=3,
            ),
        ]
