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
            "init": "project_init_request",
            "save": "project_update_request",
            "run":  "engine_run_request",
            "stop": "engine_stop_request",
            "move": "node_update_request",
            "clear_venvs": "clean_all_venvs_request"  # <--- Added this
        }

        signal_name = mapping.get(cmd)
        if signal_name:
            # The ExecutionManager is listening for 'clean_all_venvs_request'
            signal_hub.emit(signal_name, payload)
            return {"status": "dispatched", "signal": signal_name}

        return {"status": "error", "message": f"Unknown command: {cmd}"}

    return router