from __future__ import annotations

from .registry import PermissionLevel, ToolDefinition, ToolRegistry
from .shell import execute_command


def register_git_github_tools(registry: ToolRegistry) -> None:
    registry.register(ToolDefinition("git_status", "Git status.", {"type": "object", "properties": {}}, {}, PermissionLevel.READ_ONLY, func=lambda: execute_command("git status")))
