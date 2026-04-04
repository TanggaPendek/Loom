"""
ws_client.py — Loom Engine WebSocket Client
--------------------------------------------
Thin async wrapper used by the engine to send state events to ws_service.py.
Safe: if the WS service is unavailable, engine continues without crashing.
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from typing import Optional

WS_URL = "ws://localhost:8001/engine"


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


class EngineWSClient:
    def __init__(self):
        self._ws = None
        self._connected = False

    async def connect(self, retries: int = 5, delay: float = 0.5) -> bool:
        """Attempt to connect to ws_service. Returns True on success."""
        try:
            import websockets
        except ImportError:
            print("[WS-CLIENT] 'websockets' not installed — WS disabled")
            return False

        for attempt in range(1, retries + 1):
            try:
                self._ws = await websockets.connect(WS_URL)
                self._connected = True
                print(f"[WS-CLIENT] Connected to {WS_URL}")
                sys.stdout.flush()
                return True
            except Exception as e:
                print(f"[WS-CLIENT] Connect attempt {attempt}/{retries} failed: {e}")
                sys.stdout.flush()
                if attempt < retries:
                    await asyncio.sleep(delay)

        print("[WS-CLIENT] Could not connect to WS service — engine will continue without WS")
        sys.stdout.flush()
        return False

    async def send(self, event: str, data: dict = None):
        """Send an event message. No-op if not connected."""
        if not self._connected or self._ws is None:
            return
        try:
            payload = json.dumps({
                "event": event,
                "data": data or {},
                "ts": _ts()
            })
            await self._ws.send(payload)
        except Exception as e:
            print(f"[WS-CLIENT] Send failed ({event}): {e}")
            self._connected = False

    async def close(self):
        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
        self._connected = False


# Module-level singleton — set by main_engine after connect
_client: Optional[EngineWSClient] = None


def get_client() -> Optional[EngineWSClient]:
    return _client


def set_client(client: Optional[EngineWSClient]):
    global _client
    _client = client
