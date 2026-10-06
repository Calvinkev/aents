from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import AsyncGenerator, Dict, List

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter()
_event_queues: List[asyncio.Queue] = []


def broadcast_event(event_type: str, data: Dict) -> None:
    payload = {"event": event_type, "timestamp": time.time(), "data": data}
    for q in _event_queues:
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            pass


async def event_generator() -> AsyncGenerator[str, None]:
    queue = asyncio.Queue(maxsize=100)
    _event_queues.append(queue)
    try:
        yield f"data: {json.dumps({'event': 'CONNECTED', 'message': 'Subscribed to AENTS real-time event stream.'})}\n\n"
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        if queue in _event_queues:
            _event_queues.remove(queue)


@router.get("/api/v1/events")
async def stream_events():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
