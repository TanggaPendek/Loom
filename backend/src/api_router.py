from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any

def create_dispatcher(signal_hub, project_backend, log_manager=None):
    router = APIRouter()


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
        print("COMMAND_MAP KEYS:", list(COMMAND_MAP.keys()))

        
        if not signal_name:
            return {"status": "error", "message": f"Unknown action: {cmd}"}
        
        results = signal_hub.emit(signal_name, payload)
        print(f"DEBUG: Signal {signal_name} returned results: {results}")
        
        # Check if we got any results
        if not results or len(results) == 0:
            return {"status": "error", "message": f"No handlers registered for {cmd}"}
        
        # Get the first result
        result = results[0]
        
        # If handler returned None, that's an error
        if result is None:
            return {"status": "error", "message": f"Handler for {cmd} returned no data"}
        
        # If handler returned a dict with status, use it
        if isinstance(result, dict):
            if result.get("status") == "ok":
                return {"status": "success", "command": cmd, **result}
            elif result.get("status") == "error":
                return result  # Return error as-is
            else:
                # Has dict but no status field - assume success
                return {"status": "success", "command": cmd, "result": result}
        
        # Handler returned something else (string, number, etc)
        return {"status": "success", "command": cmd, "result": result}

    @router.get("/sync/{target}")
    async def sync_data(target: str, since: str = None):
        """Data-fetching requests"""
        # Special handling for logs (uses log_manager directly)
        if target == "logs" and log_manager:
            logs = log_manager.get_logs(since_timestamp=since)
            return {"status": "ok", "logs": logs}
        
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