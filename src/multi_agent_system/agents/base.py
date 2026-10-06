from __future__ import annotations

from dataclasses import dataclass, field
import logging
import time
from typing import Any, Dict, List, Optional

from ..llm.prompts import PromptBuilder
from ..llm.provider import LLMProvider, LLMResponse, get_llm_provider
from ..tools.registry import ToolExecutionResult, ToolRegistry

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    agent_id: str
    task_id: str
    subtask_id: str
    status: str
    output: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.8
    tokens_used: int = 0
    estimated_cost: float = 0.0
    latency_ms: int = 0
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class BaseAgent:
    name: str = "base_agent"
    description: str = "Base AI Agent"
    capabilities: List[str] = []

    def __init__(self, llm_provider: Optional[LLMProvider] = None, tool_registry: Optional[ToolRegistry] = None):
        self.llm_provider = llm_provider or get_llm_provider()
        self.tool_registry = tool_registry or ToolRegistry()

    async def run(self, task_id: str, subtask_id: str, task_description: str, context: str = "", guidance: str = "") -> AgentResult:
        start_time = time.time()
        messages = PromptBuilder.format_agent_prompt(
            agent_role=f"{self.name}: {self.description}",
            system_rules=f"Capabilities: {', '.join(self.capabilities)}.",
            user_task=task_description,
            context=context,
            guidance=guidance,
        )

        llm_res: LLMResponse = await self.llm_provider.generate(messages=messages)
        latency = int((time.time() - start_time) * 1000)

        return AgentResult(
            agent_id=self.name,
            task_id=task_id,
            subtask_id=subtask_id,
            status="success",
            output=llm_res.content,
            evidence=["LLM reasoning"],
            confidence=0.85,
            tokens_used=llm_res.total_tokens,
            estimated_cost=llm_res.estimated_cost,
            latency_ms=latency,
        )
