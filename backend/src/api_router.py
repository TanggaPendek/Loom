from fastapi import APIRouter, Body
from typing import Dict, Any

def create_dispatcher(signal_hub, project_backend):
    router = APIRouter()

    @router.post("/dispatch")
    async def dispatch(payload: Dict[str, Any] = Body(...)):
        """
        Single entry point for all frontend commands.
        Example payload: {"cmd": "move", "id": "n1", "x": 100}
        """
        cmd = payload.get("cmd")
        
        # 1. Map simple commands to SignalHub events
        mapping = {
            "init": "project_init_request",
            "save": "project_update_request",
            "run":  "engine_run_request",
            "stop": "engine_stop_request",
            "move": "node_update_request", # Example for the 1px move
        }

        signal_name = mapping.get(cmd)
        if signal_name:
            # Emit the signal. The appropriate Manager is already listening.
            signal_hub.emit(signal_name, payload)
            return {"status": "dispatched", "signal": signal_name}

        return {"status": "error", "message": f"Unknown command: {cmd}"}

    return router