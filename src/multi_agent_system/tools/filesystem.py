from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from .registry import PermissionLevel, ToolDefinition, ToolRegistry


def _resolve_safe_path(path_str: str, root_dir: Optional[str] = None) -> Path:
    root = Path(root_dir or os.getcwd()).resolve()
    target = (root / path_str).resolve() if not Path(path_str).is_absolute() else Path(path_str).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise PermissionError(f"Access denied: Path '{path_str}' escapes workspace boundary '{root}'.")
    return target


def list_files(path: str = ".", root_dir: Optional[str] = None) -> str:
    safe_p = _resolve_safe_path(path, root_dir)
    if not safe_p.exists(): return f"Error: Path '{path}' does not exist."
    return "\n".join(f"{'[DIR]' if item.is_dir() else '[FILE]'} {item.name}" for item in sorted(safe_p.iterdir()))


def read_file(path: str, root_dir: Optional[str] = None) -> str:
    safe_p = _resolve_safe_path(path, root_dir)
    return safe_p.read_text(encoding="utf-8", errors="replace")


def register_filesystem_tools(registry: ToolRegistry, root_dir: Optional[str] = None) -> None:
    registry.register(ToolDefinition("list_files", "List files safely.", {"type": "object", "properties": {"path": {"type": "string", "default": "."}}}, {}, PermissionLevel.READ_ONLY, func=lambda path=".": list_files(path, root_dir)))
    registry.register(ToolDefinition("read_file", "Read file safely.", {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}, {}, PermissionLevel.READ_ONLY, func=lambda path: read_file(path, root_dir)))
