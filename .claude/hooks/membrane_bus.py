# Helper to publish membrane.inject envelopes from Claude Code hooks.
#
# Hooks run inside short-lived processes; we provide a lightweight
# singleton that reuses a single WebSocket connection behind the scenes
# so parallel hooks do not spawn competing sockets.

from __future__ import annotations

import asyncio
import atexit
import json
import os
import sys
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import websockets  # type: ignore[import]


def _utc_ts() -> str:
    return datetime.utcnow().isoformat(timespec="milliseconds") + "Z"


def _default_org() -> str:
    return os.getenv("MEMBRANE_ORG", "dev-org")


def _default_inject_uri() -> str:
    return os.getenv("MEMBRANE_WS_INJECT", "ws://localhost:8765/inject")


class MembraneBusClient:
    """Shared WebSocket client with background event loop."""

    _instance: Optional["MembraneBusClient"] = None
    _instance_lock = threading.Lock()

    def __init__(self) -> None:
        self._uri = _default_inject_uri()
        self._loop = asyncio.new_event_loop()
        self._loop_ready = threading.Event()
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._async_lock: Optional[asyncio.Lock] = None
        self._thread = threading.Thread(
            target=self._run_loop,
            name="membrane-bus-client",
            daemon=True
        )
        self._thread.start()
        self._loop_ready.wait(timeout=2.0)

    @classmethod
    def instance(cls) -> "MembraneBusClient":
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._async_lock = asyncio.Lock()
        self._loop_ready.set()
        self._loop.run_forever()

    async def _ensure_connection(self) -> websockets.WebSocketClientProtocol:
        if self._ws and not self._ws.closed:
            return self._ws
        self._ws = await websockets.connect(self._uri)  # type: ignore[attr-defined]
        return self._ws

    async def _close_ws(self) -> None:
        if self._ws:
            try:
                await self._ws.close()
            finally:
                self._ws = None

    async def _send(self, envelope: Dict[str, Any]) -> None:
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()

        async with self._async_lock:
            try:
                ws = await self._ensure_connection()
                await ws.send(json.dumps(envelope))
            except Exception:
                await self._close_ws()
                ws = await self._ensure_connection()
                await ws.send(json.dumps(envelope))

    def send(self, envelope: Dict[str, Any], *, wait: bool = True, timeout: float = 5.0) -> None:
        future = asyncio.run_coroutine_threadsafe(self._send(envelope), self._loop)
        if not wait:
            return
        future.result(timeout=timeout)

    def shutdown(self) -> None:
        async def _shutdown() -> None:
            await self._close_ws()
            self._loop.stop()

        try:
            asyncio.run_coroutine_threadsafe(_shutdown(), self._loop).result(timeout=2.0)
        except Exception:
            pass
        finally:
            if self._thread.is_alive():
                self._thread.join(timeout=2.0)

    @classmethod
    def shutdown_global(cls) -> None:
        if cls._instance is not None:
            cls._instance.shutdown()
            cls._instance = None


atexit.register(MembraneBusClient.shutdown_global)


def publish_to_membrane(
    *,
    channel: str,
    payload: Dict[str, Any],
    scope: str = "organizational",
    origin: str = "ui",
    ttl_frames: int = 900,
    dedupe_key: Optional[str] = None,
    features_raw: Optional[Dict[str, float]] = None,
    suppress_errors: bool = True,
) -> None:
    """Send a membrane.inject envelope via the shared client."""
    envelope = {
        "v": "1.1",
        "type": "membrane.inject",
        "org": _default_org(),
        "id": str(uuid.uuid4()),
        "ts": _utc_ts(),
        "scope": scope,
        "channel": channel,
        "origin": origin,
        "ttl_frames": ttl_frames,
        "dedupe_key": dedupe_key or f"{channel}:{uuid.uuid4()}",
        "payload": payload,
        "sig": {
            "algo": "ed25519",
            "pubkey": os.getenv("MEMBRANE_DEV_PUBKEY", "dev-local"),
            "signature": os.getenv("MEMBRANE_DEV_SIGNATURE", "dev-local"),
        },
    }
    if features_raw:
        envelope["features_raw"] = features_raw

    try:
        MembraneBusClient.instance().send(envelope)
    except Exception as exc:  # pragma: no cover - defensive path
        if suppress_errors:
            print(f"[membrane_bus] failed to publish {channel}: {exc}", file=sys.stderr)
        else:
            raise
