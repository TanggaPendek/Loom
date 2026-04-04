"""
ws_service.py — Loom Engine WebSocket Broadcast Service
--------------------------------------------------------
Standalone asyncio WebSocket server on port 8001.
- The engine subprocess connects as a PRODUCER (sends state events).
- The frontend connects as a CONSUMER (receives broadcasts).
- All received messages are printed to the terminal for debugging.

Run standalone:   python -m executor.engine.ws_service
Or launched as a subprocess by main_engine.py automatically.
"""

import asyncio
import json
import sys
from datetime import datetime, timezone

try:
    import websockets
except ImportError:
    print("[WS-SERVICE] 'websockets' package not installed. Run: pip install websockets")
    sys.exit(1)

HOST = "localhost"
PORT = 8001

# Connected consumer frontends
_consumers: set = set()
# Single engine producer connection
_producer = None


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fmt(event: str, data: dict) -> str:
    """Pretty-print a received engine event to terminal (ASCII-only for Windows)."""
    prefix = f"[ENGINE-WS] [{_ts()}]"
    if event == "node_start":
        return f"{prefix} >> NODE START -> {data.get('nodeId', '?')}  ({data.get('name', '')})"
    elif event == "node_end":
        return f"{prefix} OK NODE END  -> {data.get('nodeId', '?')}  ({data.get('elapsed_ms', '?')}ms)"
    elif event == "node_error":
        return f"{prefix} !! NODE ERR  -> {data.get('nodeId', '?')} : {data.get('error', '')}"
    elif event == "dep_progress":
        return f"{prefix}    pip       : {data.get('line', '')}"
    elif event == "engine_finish":
        return f"{prefix} ** ENGINE FINISHED"
    elif event == "engine_error":
        return f"{prefix} !! ENGINE ERROR : {data.get('message', '')}"
    else:
        event_upper = event.upper().replace("_", " ")
        return f"{prefix} {event_upper} {json.dumps(data)}"


async def _broadcast(message: str):
    """Send a message to all connected frontend consumers."""
    dead = set()
    for ws in _consumers:
        try:
            await ws.send(message)
        except Exception:
            dead.add(ws)
    _consumers.difference_update(dead)


async def _handle_producer(websocket):
    """Handle engine connection — receive events and broadcast to consumers."""
    global _producer
    _producer = websocket
    print(f"[WS-SERVICE] Engine connected (producer)")
    try:
        async for raw in websocket:
            # Print to terminal
            try:
                msg = json.loads(raw)
                event = msg.get("event", "unknown")
                data = msg.get("data", {})
                print(_fmt(event, data))
                sys.stdout.flush()
            except Exception:
                print(f"[WS-SERVICE] Raw: {raw}")

            # Broadcast to all frontends
            await _broadcast(raw)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        _producer = None
        print(f"[WS-SERVICE] Engine disconnected")
        # Notify frontends engine is gone
        fin = json.dumps({"event": "engine_disconnect", "data": {}, "ts": _ts()})
        await _broadcast(fin)


async def _handle_consumer(websocket):
    """Handle frontend connection — just listen (no incoming data expected)."""
    _consumers.add(websocket)
    print(f"[WS-SERVICE] Frontend connected  ({len(_consumers)} total)")
    try:
        async for _ in websocket:
            pass  # consumers don't send anything
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        _consumers.discard(websocket)
        print(f"[WS-SERVICE] Frontend disconnected ({len(_consumers)} remaining)")


async def _router(websocket, path: str = "/"):
    """Route connections by path: /engine -> producer, /frontend -> consumer."""
    if path == "/engine":
        await _handle_producer(websocket)
    else:
        await _handle_consumer(websocket)


async def main():
    print(f"[WS-SERVICE] Starting on ws://{HOST}:{PORT}")
    print(f"[WS-SERVICE]   Engine   -> ws://{HOST}:{PORT}/engine")
    print(f"[WS-SERVICE]   Frontend -> ws://{HOST}:{PORT}/frontend")
    sys.stdout.flush()

    try:
        async with websockets.serve(_router, HOST, PORT):
            await asyncio.Future()  # run forever
    except OSError as e:
        print(f"[WS-SERVICE] Port {PORT} already in use — using existing instance.")
        sys.stdout.flush()
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
