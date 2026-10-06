from __future__ import annotations

import asyncio
import os
import re
from typing import Optional
from .registry import PermissionLevel, ToolDefinition, ToolRegistry

DENIED_COMMAND_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"mkfs",
    r"dd\s+if=",
    r"shutdown",
    r"reboot",
]


def _is_command_safe(cmd: str) -> bool:
    for pattern in DENIED_COMMAND_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return False
    return True


async def execute_command(command: str, timeout: float = 30.0) -> str:
    if not _is_command_safe(command):
        return "Security Error: Command denied by security policy."
    proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    return stdout.decode("utf-8", errors="replace") or stderr.decode("utf-8", errors="replace") or f"Exit code: {proc.returncode}"


def register_shell_tools(registry: ToolRegistry) -> None:
    registry.register(ToolDefinition("execute_command", "Execute command safely.", {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}, {}, PermissionLevel.SAFE_WRITE, func=execute_command))
