"""
Engine State Manager

Manages engine execution state separately from project state.
Provides simplified frontend states (idle/running) while maintaining detailed backend states.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class EngineStateManager:
    """
    Manages engine execution state with frontend/backend state separation.
    
    Backend States: idle, initializing, running, stopping, stopped, error
    Frontend States: idle, running
    
    Mapping:
    - Backend idle|stopped|error → Frontend idle
    - Backend initializing|running|stopping → Frontend running
    """
    
    def __init__(self, userdata_path: str = "userdata"):
        base_path = Path(userdata_path)
        base_path.mkdir(parents=True, exist_ok=True)
        self.state_file = base_path / "engine_state.json"
        
        # Initialize if doesn't exist
        if not self.state_file.exists():
            self._write_state({
                "status": "idle",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "project_id": None,
                "error": None,
                "process_id": None
            })
    
    def _read_state(self) -> Dict[str, Any]:
        """Read current state from file."""
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[EngineStateManager] Error reading state: {e}")
            return {
                "status": "idle",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "project_id": None,
                "error": None,
                "process_id": None
            }
    
    def _write_state(self, state: Dict[str, Any]):
        """Write state to file."""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            print(f"[EngineStateManager] Error writing state: {e}")
    
    def get_engine_state(self) -> Dict[str, Any]:
        """Get full backend engine state."""
        return self._read_state()
    
    def get_frontend_state(self) -> str:
        """
        Get simplified state for frontend UI.
        
        Returns:
            'idle' or 'running'
        """
        state = self._read_state()
        status = state.get("status", "idle")
        
        # Map backend states to frontend states
        if status in ["initializing", "running", "stopping"]:
            return "running"
        else:  # idle, stopped, error
            return "idle"
    
    def set_engine_state(
        self,
        status: str,
        project_id: Optional[str] = None,
        error: Optional[Dict[str, str]] = None,
        process_id: Optional[int] = None
    ):
        """
        Update engine state.
        
        Args:
            status: One of: idle, initializing, running, stopping, stopped, error
            project_id: Active project ID
            error: Error dict with 'message' and 'timestamp' if status is 'error'
            process_id: Process ID of running engine subprocess
        """
        valid_statuses = ["idle", "initializing", "running", "stopping", "stopped", "error"]
        if status not in valid_statuses:
            print(f"[EngineStateManager] Invalid status: {status}")
            return
        
        state = {
            "status": status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "project_id": project_id,
            "error": error,
            "process_id": process_id
        }
        
        self._write_state(state)
    
    def is_running(self) -> bool:
        """
        Check if engine is currently running.
        
        Returns:
            True if status is initializing, running, or stopping
        """
        state = self._read_state()
        status = state.get("status", "idle")
        return status in ["initializing", "running", "stopping"]
    
    def clear_error(self):
        """Clear error state and return to idle."""
        state = self._read_state()
        state["status"] = "idle"
        state["error"] = None
        state["timestamp"] = datetime.utcnow().isoformat() + "Z"
        self._write_state(state)
