"""Shared real-time visual event hub for every ATLAS interface."""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, Field

visual_router = APIRouter(prefix="/visual", tags=["ATLAS Visual Ecosystem"])

ALLOWED_EVENTS = {
    "system.ready",
    "system.alert",
    "ai.state.changed",
    "ai.speech.started",
    "ai.speech.ended",
    "council.started",
    "council.completed",
    "project.progress.changed",
    "research.ingestion.changed",
    "twin.simulation.changed",
    "weaver.plan.changed",
    "robot.telemetry.changed",
    "hud.mode.changed",
}
ALLOWED_PERSONAS = {"ajani", "minerva", "hermes", "council", "atlas"}
ALLOWED_STATES = {
    "idle", "listening", "thinking", "speaking", "working",
    "warning", "error", "offline",
}


class VisualPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    persona: Optional[str] = None
    state: Optional[str] = None
    emotion: Optional[str] = None
    intensity: Optional[float] = Field(default=None, ge=0, le=1)
    mode: Optional[str] = None
    message: Optional[str] = None
    progress: Optional[float] = Field(default=None, ge=0, le=1)
    data: Optional[Dict[str, Any]] = None


class VisualEventCreate(BaseModel):
    event: str
    payload: VisualPayload = Field(default_factory=VisualPayload)
    source: str = "atlas-core"
    correlation_id: Optional[str] = None


class VisualHub:
    def __init__(self) -> None:
        self._clients: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
        self._last_event: Optional[Dict[str, Any]] = None

    @property
    def client_count(self) -> int:
        return len(self._clients)

    @property
    def last_event(self) -> Optional[Dict[str, Any]]:
        return self._last_event

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._clients.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(websocket)

    async def broadcast(self, envelope: Dict[str, Any]) -> int:
        self._last_event = envelope
        async with self._lock:
            clients = tuple(self._clients)

        stale = []
        delivered = 0
        for client in clients:
            try:
                await client.send_json(envelope)
                delivered += 1
            except Exception:
                stale.append(client)

        if stale:
            async with self._lock:
                for client in stale:
                    self._clients.discard(client)
        return delivered


hub = VisualHub()


def build_envelope(request: VisualEventCreate) -> Dict[str, Any]:
    payload = request.payload.model_dump(exclude_none=True)
    if request.event not in ALLOWED_EVENTS:
        raise HTTPException(422, f"Unsupported visual event: {request.event}")
    if payload.get("persona") not in ALLOWED_PERSONAS | {None}:
        raise HTTPException(422, "Unknown ATLAS persona")
    if payload.get("state") not in ALLOWED_STATES | {None}:
        raise HTTPException(422, "Unknown ATLAS visual state")

    return {
        "version": "1.0",
        "event": request.event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": request.source,
        "correlation_id": request.correlation_id or str(uuid.uuid4()),
        "payload": payload,
    }


@visual_router.get("/status")
async def visual_status() -> Dict[str, Any]:
    return {
        "status": "ready",
        "protocol_version": "1.0",
        "connected_clients": hub.client_count,
        "last_event": hub.last_event,
    }


@visual_router.post("/events")
async def publish_visual_event(request: VisualEventCreate) -> Dict[str, Any]:
    envelope = build_envelope(request)
    delivered = await hub.broadcast(envelope)
    return {"delivered": delivered, "event": envelope}


@visual_router.websocket("/ws")
async def visual_websocket(websocket: WebSocket) -> None:
    await hub.connect(websocket)
    ready = build_envelope(VisualEventCreate(
        event="system.ready",
        source="atlas-core",
        payload=VisualPayload(
            persona="atlas",
            state="idle",
            message="ATLAS visual bridge connected",
        ),
    ))
    await websocket.send_json(ready)

    try:
        while True:
            incoming = await websocket.receive_json()
            request = VisualEventCreate.model_validate(incoming)
            envelope = build_envelope(request)
            await hub.broadcast(envelope)
    except WebSocketDisconnect:
        await hub.disconnect(websocket)
    except Exception:
        await hub.disconnect(websocket)
        await websocket.close(code=1003)
