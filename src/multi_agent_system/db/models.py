from __future__ import annotations

import datetime
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued")
    priority: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)


class TaskRun(Base):
    __tablename__ = "task_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False)
    trace_id: Mapped[str] = mapped_column(String(36), default=generate_uuid)
    status: Mapped[str] = mapped_column(String(50), default="running")
    iterations: Mapped[int] = mapped_column(Integer, default=0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    final_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
