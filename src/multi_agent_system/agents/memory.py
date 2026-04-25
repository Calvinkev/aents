from __future__ import annotations

from typing import Dict, List


class MemoryLearningAgent:
    def __init__(self) -> None:
        self.route_history: List[Dict[str, float]] = []

    def record(self, specialist_name: str, success: bool, score: float, cost: float, latency_ms: int) -> None:
        self.route_history.append(
            {
                "specialist": specialist_name,
                "success": 1.0 if success else 0.0,
                "score": score,
                "cost": cost,
                "latency_ms": float(latency_ms),
            }
        )

    def summary(self) -> Dict[str, float]:
        if not self.route_history:
            return {"records": 0.0, "success_rate": 0.0, "avg_cost": 0.0, "avg_latency_ms": 0.0}

        records = len(self.route_history)
        success_rate = sum(x["success"] for x in self.route_history) / records
        avg_cost = sum(x["cost"] for x in self.route_history) / records
        avg_latency = sum(x["latency_ms"] for x in self.route_history) / records
        return {
            "records": float(records),
            "success_rate": success_rate,
            "avg_cost": avg_cost,
            "avg_latency_ms": avg_latency,
        }
