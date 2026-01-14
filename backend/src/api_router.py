from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any

def create_dispatcher(signal_hub, project_backend):
    router = APIRouter()

    COMMAND_MAP = {
        # init = HOT RELOAD EVERYTHING
        "init": "hot_reload_all",

        # explicit reloads (optional but useful)
        "reload_projects": "project_hot_reload",
        "reload_nodes": "node_hot_reload",

        # project ops
        "project_create": "project_create_request",
        "project_edit":   "project_update_request",
        "project_delete": "project_delete_request",
        "load_graph": "load_graph_request",

        # node ops
        "node_add":    "node_create_request",
        "node_edit":   "node_update_request",
        "node_delete": "node_delete_request",
        "node_move":   "node_move_request",

        # engine
        "run":        "engine_run_request",
        "stop":       "engine_stop_request",
        "force_stop": "engine_kill_request",
    }
    SYNC_MAP = {
        "startup": "startup_request",
        "load_graph": "load_graph_request",
        "node_index": "node_index_request"
    }

    @router.post("/dispatch")
    async def dispatch(payload: Dict[str, Any] = Body(...)):
        """Fire-and-forget actions"""
        cmd = payload.get("cmd")
        signal_name = COMMAND_MAP.get(cmd)
        
        if not signal_name:
            return {"status": "error", "message": f"Unknown action: {cmd}"}

        signal_hub.emit_concurrent(signal_name, payload)
        return {"status": "success", "command": cmd}

    @router.get("/sync/{target}")
    async def sync_data(target: str):
        """Data-fetching requests"""
        signal_name = SYNC_MAP.get(target)
        
        if not signal_name:
            raise HTTPException(status_code=404, detail=f"Sync target '{target}' not mapped")

        # Capture the results from the updated emit()
        results = signal_hub.emit(signal_name, {})
        
        # If the handler returned a dictionary, it's at results[0]
        if results and results[0] is not None:
            return results[0]

        return {"status": "error", "message": "No data returned from handler"}

    return router