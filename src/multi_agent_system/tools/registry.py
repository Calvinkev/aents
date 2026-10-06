from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class PermissionLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    SAFE_WRITE = "SAFE_WRITE"
    DANGEROUS_WRITE = "DANGEROUS_WRITE"
    ADMIN = "ADMIN"


PERMISSION_RANK = {PermissionLevel.READ_ONLY: 1, PermissionLevel.SAFE_WRITE: 2, PermissionLevel.DANGEROUS_WRITE: 3, PermissionLevel.ADMIN: 4}


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    permission_level: PermissionLevel
    timeout_seconds: float = 30.0
    require_approval: bool = False
    func: Optional[Callable[..., Any]] = None


@dataclass
class ToolExecutionResult:
    tool_name: str
    success: bool
    output: str
    error: Optional[str] = None
    latency_ms: int = 0


class ToolRegistry:
    def __init__(self, max_allowed_level: PermissionLevel = PermissionLevel.DANGEROUS_WRITE):
        self._tools: Dict[str, ToolDefinition] = {}
        self.max_allowed_level = max_allowed_level

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        return [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.input_schema}} for t in self._tools.values()]

    async def execute(self, name: str, parameters: Dict[str, Any], max_level: Optional[PermissionLevel] = None) -> ToolExecutionResult:
        tool = self.get(name)
        if not tool:
            return ToolExecutionResult(tool_name=name, success=False, output="", error=f"Tool '{name}' not found.")
        allowed_level = max_level or self.max_allowed_level
        if PERMISSION_RANK[tool.permission_level] > PERMISSION_RANK[allowed_level]:
            return ToolExecutionResult(tool_name=name, success=False, output="", error=f"Permission denied for tool '{name}'.")
        try:
            if asyncio.iscoroutinefunction(tool.func):
                res = await asyncio.wait_for(tool.func(**parameters), timeout=tool.timeout_seconds)
            else:
                res = await asyncio.wait_for(asyncio.to_thread(tool.func, **parameters), timeout=tool.timeout_seconds)
            return ToolExecutionResult(tool_name=name, success=True, output=str(res))
        except Exception as e:
            return ToolExecutionResult(tool_name=name, success=False, output="", error=str(e))
