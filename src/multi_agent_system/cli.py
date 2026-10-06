from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from .agent_registry import AgentRegistry
from .config_loader import load_config
from .orchestrator import Orchestrator
from .tools.filesystem import register_filesystem_tools
from .tools.git_github import register_git_github_tools
from .tools.http_db import register_http_db_tools
from .tools.registry import ToolRegistry
from .tools.shell import register_shell_tools


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aents",
        description="AENTS - Production AI Agent Orchestration Platform CLI",
    )
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument(
        "--config",
        default="config/system_config.yaml",
        help="Path to system config YAML",
    )

    subparsers = parser.add_subparsers(dest="command", help="CLI Subcommands")

    # aents run
    run_parser = subparsers.add_parser("run", help="Run a task on the platform")
    run_parser.add_argument("task", help="Task description to execute")
    run_parser.add_argument("--show-trace", action="store_true", help="Display full execution trace")
    run_parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    # aents status
    status_parser = subparsers.add_parser("status", help="Check status of a task")
    status_parser.add_argument("task_id", help="Task ID")
    status_parser.add_argument("--json", action="store_true")

    # aents trace
    trace_parser = subparsers.add_parser("trace", help="View execution trace of a task")
    trace_parser.add_argument("task_id", help="Task ID")
    trace_parser.add_argument("--json", action="store_true")

    # aents agents
    agents_parser = subparsers.add_parser("agents", help="List all registered specialist agents")
    agents_parser.add_argument("--json", action="store_true")

    # aents tools
    tools_parser = subparsers.add_parser("tools", help="List all registered tools")
    tools_parser.add_argument("--json", action="store_true")

    # aents cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a running task")
    cancel_parser.add_argument("task_id", help="Task ID to cancel")
    cancel_parser.add_argument("--json", action="store_true")

    return parser


def main() -> None:
    parser = create_parser()

    if len(sys.argv) > 1 and sys.argv[1].startswith("--task"):
        legacy_parser = argparse.ArgumentParser()
        legacy_parser.add_argument("--task", required=True)
        legacy_parser.add_argument("--config", default="config/system_config.yaml")
        legacy_parser.add_argument("--show-trace", action="store_true")
        args = legacy_parser.parse_args()

        config = load_config(args.config)
        orc = Orchestrator(config=config)
        state = orc.run(args.task)

        print("=== FINAL OUTPUT ===")
        print(state.final_output)
        print("\n=== STATUS ===")
        print(f"completed={state.completed}, escalated={state.escalated}, iterations={state.iteration}")
        if args.show_trace:
            print("\n=== TRACE ===")
            print(json.dumps(state.traces, indent=2))
        return

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    config = load_config(args.config)
    output_json = getattr(args, "json", False)

    if args.command == "run":
        orc = Orchestrator(config=config)
        state = orc.run(args.task)

        if output_json:
            out = {
                "task_id": state.task_id,
                "task": state.task,
                "completed": state.completed,
                "escalated": state.escalated,
                "iterations": state.iteration,
                "final_output": state.final_output,
                "traces": state.traces,
            }
            print(json.dumps(out, indent=2))
        else:
            print("=== FINAL OUTPUT ===")
            print(state.final_output)
            print("\n=== STATUS ===")
            print(f"completed={state.completed}, escalated={state.escalated}, iterations={state.iteration}")
            if getattr(args, "show_trace", False):
                print("\n=== TRACE ===")
                print(json.dumps(state.traces, indent=2))

    elif args.command == "agents":
        reg = AgentRegistry()
        specialists = reg.list_specialists()
        if output_json:
            out = [
                {
                    "name": s.name,
                    "capabilities": s.capabilities,
                    "success_rate": s.success_rate,
                    "avg_latency_ms": s.avg_latency_ms,
                    "avg_cost": s.avg_cost,
                }
                for s in specialists
            ]
            print(json.dumps(out, indent=2))
        else:
            print("=== REGISTERED SPECIALIST AGENTS ===")
            for s in specialists:
                print(f"• {s.name.upper()}")
                print(f"  Capabilities: {', '.join(s.capabilities)}")
                print(f"  Success Rate: {s.success_rate*100:.0f}% | Avg Latency: {s.avg_latency_ms:.0f}ms | Avg Cost: ${s.avg_cost:.2f}\n")

    elif args.command == "tools":
        tool_reg = ToolRegistry()
        register_filesystem_tools(tool_reg)
        register_shell_tools(tool_reg)
        register_git_github_tools(tool_reg)
        register_http_db_tools(tool_reg)

        tools = tool_reg.list_tools()
        if output_json:
            out = [
                {
                    "name": t.name,
                    "description": t.description,
                    "permission_level": t.permission_level.value,
                    "require_approval": t.require_approval,
                    "schema": t.input_schema,
                }
                for t in tools
            ]
            print(json.dumps(out, indent=2))
        else:
            print("=== REGISTERED TOOLS ===")
            for t in tools:
                appr = " [Requires Approval]" if t.require_approval else ""
                print(f"• {t.name} ({t.permission_level.value}){appr}")
                print(f"  Description: {t.description}\n")

    elif args.command in ("status", "trace", "cancel"):
        if output_json:
            print(json.dumps({"task_id": args.task_id, "status": "queued", "message": "Query API for task info"}))
        else:
            print(f"Task ID #{args.task_id} command '{args.command}' issued.")


if __name__ == "__main__":
    main()
