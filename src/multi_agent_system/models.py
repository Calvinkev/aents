from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ValidationStatus(str, Enum):
    PASS = "pass"
    SOFT_FAIL = "soft_fail"
    HARD_FAIL = "hard_fail"


@dataclass
class Subtask:
    id: str
    title: str
    objective: str
    acceptance_criteria: List[str]
    priority: int = 1


@dataclass
class CandidateResult:
    subtask_id: str
    content: str
    evidence: List[str]
    confidence: float
    estimated_cost: float
    estimated_latency_ms: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    status: ValidationStatus
    score: float
    reasons: List[str]
    suggested_fixes: List[str]


@dataclass
class RouteDecision:
    specialist_name: str
    route_score: float
    rationale: str


@dataclass
class TaskState:
    task: str
    iteration: int = 0
    completed: bool = False
    escalated: bool = False
    final_output: Optional[str] = None
    traces: List[Dict[str, Any]] = field(default_factory=list)
