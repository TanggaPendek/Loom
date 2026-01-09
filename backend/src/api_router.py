from fastapi import APIRouter, Body
from typing import Dict, Any

def create_dispatcher(signal_hub, project_backend):
    router = APIRouter()

    @router.post("/dispatch")
    async def dispatch(payload: Dict[str, Any] = Body(...)):
        """
        Single entry point for all frontend commands.
        """
        cmd = payload.get("cmd")
        
        # Mapping frontend commands to SignalHub events
        mapping = {
            # Initialization
            "init": "project_load_config_request",
            
            # Project Management
            "project_create": "project_create_request",
            "project_edit":   "project_update_request",
            "project_delete": "project_delete_request",
            
            # Node Operations
            "node_add":    "node_create_request",
            "node_edit":   "node_update_request",
            "node_delete": "node_delete_request",
            "node_move":   "node_move_request",
            "init_nodes": "node_bank_request",
            
            # Engine Control
            "run":        "engine_run_request",
            "stop":       "engine_stop_request",
            "force_stop": "engine_kill_request",
        }

        signal_name = mapping.get(cmd)
        if signal_name:
            # The ExecutionManager is listening for 'clean_all_venvs_request'
            signal_hub.emit(signal_name, payload)
            return {"status": "dispatched", "signal": signal_name}

        return {"status": "error", "message": f"Unknown command: {cmd}"}

    return router