from __future__ import annotations

import argparse
import json

from .config_loader import load_config
from .orchestrator import Orchestrator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run multi-agent AI system for [task]")
    parser.add_argument("--task", required=True, help="Task description to execute")
    parser.add_argument(
        "--config",
        default="config/system_config.yaml",
        help="Path to system config YAML",
    )
    parser.add_argument(
        "--show-trace",
        action="store_true",
        help="Print execution trace JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    orchestrator = Orchestrator(config=config)
    state = orchestrator.run(task=args.task)

    print("=== FINAL OUTPUT ===")
    print(state.final_output)
    print("\n=== STATUS ===")
    print(f"completed={state.completed}, escalated={state.escalated}, iterations={state.iteration}")

    if args.show_trace:
        print("\n=== TRACE ===")
        print(json.dumps(state.traces, indent=2))


if __name__ == "__main__":
    main()
