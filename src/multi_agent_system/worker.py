from __future__ import annotations

import asyncio
import logging
from typing import Dict, Optional

from .api.events import broadcast_event
from .config_loader import load_config
from .orchestrator import Orchestrator

logger = logging.getLogger(__name__)


class TaskWorker:
    def __init__(self, config_path: str = "config/system_config.yaml"):
        self.config = load_config(config_path)
        self.running = False
        self.queue = asyncio.Queue()

    def handle_event(self, event_type: str, data: Dict) -> None:
        broadcast_event(event_type, data)

    async def enqueue_task(self, task_id: str, task_description: str) -> None:
        await self.queue.put((task_id, task_description))

    async def start(self) -> None:
        self.running = True
        while self.running:
            try:
                task_id, task_description = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                orchestrator = Orchestrator(config=self.config, event_callback=self.handle_event)
                await orchestrator.run_async(task_description, task_id=task_id)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue

    def stop(self) -> None:
        self.running = False
