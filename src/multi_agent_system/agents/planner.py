from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from ..llm.prompts import PromptBuilder
from ..llm.provider import LLMProvider, get_llm_provider
from ..models import Subtask

logger = logging.getLogger(__name__)


class PlannerAgent:
    """LLM-powered planner agent that decomposes complex user tasks into a subtask DAG."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider or get_llm_provider()

    async def plan_dag(self, task: str) -> List[Subtask]:
        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "You are the Planner Agent in AENTS. Decompose the user request into an optimal "
                    "execution-directed DAG of subtasks.\n"
                    "Respond with a JSON object containing a 'subtasks' list:\n"
                    "{\n"
                    "  'subtasks': [\n"
                    "    {\n"
                    "      'id': 's1',\n"
                    "      'title': '...', \n"
                    "      'objective': '...',\n"
                    "      'dependencies': [],\n"
                    "      'required_capabilities': ['research'],\n"
                    "      'acceptance_criteria': ['Criterion 1']\n"
                    "    }\n"
                    "  ]\n"
                    "}"
                ),
            },
            {"role": "user", "content": f"User Task: {task}"},
        ]

        try:
            res = await self.llm_provider.generate(
                messages=prompt_messages,
                response_format={"type": "json_object"},
            )
            data = json.loads(res.content)
            subtasks_json = data.get("subtasks", [])

            subtasks: List[Subtask] = []
            for i, st in enumerate(subtasks_json, 1):
                subtasks.append(
                    Subtask(
                        id=st.get("id", f"s{i}"),
                        title=st.get("title", f"Subtask {i}"),
                        objective=st.get("objective", f"Objective for subtask {i}"),
                        acceptance_criteria=st.get(
                            "acceptance_criteria",
                            ["Explicit intent", "Valid output"],
                        ),
                        priority=i,
                        dependencies=st.get("dependencies", []),
                        required_capabilities=st.get("required_capabilities", []),
                    )
                )

            if subtasks:
                return subtasks

        except Exception as e:
            logger.warning(f"LLM planning failed or returned invalid JSON ({e}). Falling back to default plan.")

        return self._default_fallback_plan(task)

    def plan(self, task: str) -> List[Subtask]:
        try:
            return asyncio.run(self.plan_dag(task))
        except RuntimeError:
            return self._default_fallback_plan(task)

    def _default_fallback_plan(self, task: str) -> List[Subtask]:
        return [
            Subtask(
                id="s1",
                title="Inspect Environment & Context",
                objective=f"Analyze task requirements and repository context for: {task}",
                acceptance_criteria=[
                    "Intent is explicit",
                    "Constraints and environment are identified",
                ],
                priority=1,
                dependencies=[],
                required_capabilities=["research", "code_analysis"],
            ),
            Subtask(
                id="s2",
                title="Execute Solution Strategy",
                objective=f"Implement, modify code, or perform analysis for: {task}",
                acceptance_criteria=[
                    "Core deliverable produced",
                    "Reasoning and tests pass acceptance criteria",
                ],
                priority=2,
                dependencies=["s1"],
                required_capabilities=["coding", "debugging", "data_analysis"],
            ),
            Subtask(
                id="s3",
                title="Validate & Summarize Output",
                objective=f"Verify evidence and finalize response for: {task}",
                acceptance_criteria=[
                    "Actionable conclusions and evidence present",
                ],
                priority=3,
                dependencies=["s2"],
                required_capabilities=["general_reasoning"],
            ),
        ]
