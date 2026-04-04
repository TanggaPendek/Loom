from fastapi import APIRouter, Body, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
import asyncio
import json


# ── WebSocket Connection Manager ──────────────────────────────────────────────

class _ConnectionManager:
    """Broadcast engine status messages to all connected WS clients."""

    def __init__(self):
        self.active: List[WebSocket] = []
        self._loop = None

    def _get_loop(self):
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
        return self._loop

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def _send(self, ws: WebSocket, data: str):
        try:
            await ws.send_text(data)
        except Exception:
            self.disconnect(ws)

    def broadcast(self, payload: dict):
        """Thread-safe broadcast — called from signal_hub (sync thread)."""
        data = json.dumps(payload)
        loop = self._get_loop()
        for ws in list(self.active):
            asyncio.run_coroutine_threadsafe(self._send(ws, data), loop)


# Module-level singleton
ws_manager = _ConnectionManager()

# Guard: wire signal_hub → WS exactly once
_ws_registered = False


def _register_ws_listeners(signal_hub):
    global _ws_registered
    if _ws_registered:
        return
    _ws_registered = True

    def _on_started(payload):
        ws_manager.broadcast({"type": "engine_status", "status": "running",
                               "message": "Engine started"})

    def _on_output(payload):
        line = payload.get("line") or payload.get("message", "")
        if line:
            ws_manager.broadcast({"type": "engine_status", "status": "running",
                                   "message": line})

    def _on_finished(payload):
        code = payload.get("exit_code", 0)
        ws_manager.broadcast({"type": "engine_status", "status": "idle",
                               "message": f"Engine finished (exit {code})"})

    def _on_error(payload):
        err = payload.get("error", "Unknown error")
        ws_manager.broadcast({"type": "engine_status", "status": "idle",
                               "message": f"Engine error: {err}"})

    signal_hub.on("execution_started",  _on_started)
    signal_hub.on("execution_output",   _on_output)
    signal_hub.on("execution_finished", _on_finished)
    signal_hub.on("execution_error",    _on_error)


# ── Router Factory ────────────────────────────────────────────────────────────

def create_dispatcher(signal_hub, project_backend, log_manager=None):
    router = APIRouter()

    # Wire WS broadcast listeners (no-op after first call)
    _register_ws_listeners(signal_hub)

    COMMAND_MAP = {
        "init": "hot_reload_all",
        "reload_projects": "project_hot_reload",
        "reload_nodes": "node_hot_reload",
        "project_create": "project_create_request",
        "project_edit": "project_update_request",
        "project_delete": "project_delete_request",
        "project_load": "project_load_request",
        "load_graph": "load_graph_request",

        "graph_node_add": "project_node_add",
        "graph_node_delete": "project_node_delete",
        "graph_node_update_input": "graph_node_update_input_request",
        "graph_node_edit": "graph_node_move_request",

        "connection_create": "connection_create_request",
        "connection_delete": "connection_delete_request",

        "node_add": "node_create_request",
        "node_edit": "node_update_request",
        "node_delete": "node_delete_request",
        "node_move": "node_move_request",

        "run": "engine_run_request",
        "stop": "engine_stop_request",
        "force_stop": "engine_kill_request",

        "engine_get_state": "engine_state_request",
        "engine_get_logs": "engine_logs_request",
    }

    SYNC_MAP = {
        "startup": "startup_request",
        "load_graph": "load_graph_request",
        "node_index": "node_index_request",
        "logs": "get_logs"
    }

    @router.post("/dispatch")
    async def dispatch(payload: Dict[str, Any] = Body(...)):
        cmd = payload.get("cmd")
        signal_name = COMMAND_MAP.get(cmd)
        print("CMD RECEIVED:", cmd)

        if not signal_name:
            return {"status": "error", "message": f"Unknown action: {cmd}"}

        results = signal_hub.emit(signal_name, payload)

        if not results or len(results) == 0:
            return {"status": "error", "message": f"No handlers registered for {cmd}"}

        result = results[0]

        if result is None:
            return {"status": "error", "message": f"Handler for {cmd} returned no data"}

        if isinstance(result, dict):
            if result.get("status") == "ok":
                return {"status": "success", "command": cmd, **result}
            elif result.get("status") == "error":
                return result
            else:
                return {"status": "success", "command": cmd, "result": result}

        return {"status": "success", "command": cmd, "result": result}

    @router.get("/sync/{target}")
    async def sync_data(target: str, since: str = None):
        """Data-fetching requests"""
        if target == "logs" and log_manager:
            logs = log_manager.get_logs(since_timestamp=since)
            return {"status": "ok", "logs": logs}

        signal_name = SYNC_MAP.get(target)

        if not signal_name:
            raise HTTPException(status_code=404, detail=f"Sync target '{target}' not mapped")

        results = signal_hub.emit(signal_name, {})

        if results and results[0] is not None:
            return results[0]

        return {"status": "error", "message": "No data returned from handler"}

    return router