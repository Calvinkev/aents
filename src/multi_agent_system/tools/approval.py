from __future__ import annotations

from dataclasses import dataclass, field
import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class ApprovalStatus(str, Enum):
    PROPOSED = "PROPOSED"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class ApprovalRequestItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_run_id: str = ""
    agent_id: str = ""
    tool_name: str = ""
    action_summary: str = ""
    status: ApprovalStatus = ApprovalStatus.WAITING_FOR_APPROVAL


class ApprovalManager:
    def __init__(self):
        self._pending: Dict[str, ApprovalRequestItem] = {}

    def create_request(self, task_run_id: str, agent_id: str, tool_name: str, action_summary: str) -> ApprovalRequestItem:
        req = ApprovalRequestItem(task_run_id=task_run_id, agent_id=agent_id, tool_name=tool_name, action_summary=action_summary)
        self._pending[req.id] = req
        return req

    def list_pending(self) -> List[ApprovalRequestItem]:
        return list(self._pending.values())


global_approval_manager = ApprovalManager()
