"""
Loom Log Manager

Manages execution logs for displaying in the frontend UI.
These are "selected logs" - intentional log_print() calls from node scripts,
not full execution logs or debug output.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class LogManager:
    """
    Manages execution logs for frontend display.
    
    Logs are stored per-project and cleared on each execution start.
    """
    
    def __init__(self, project_base_path: Path):
        """
        Initialize LogManager.
        
        Args:
            project_base_path: Base path for userdata (where projects are stored)
        """
        self.project_base_path = project_base_path
        self.current_log_file: Optional[Path] = None
    
    def set_active_project(self, project_name: str) -> None:
        """
        Set the active project for logging.
        
        Args:
            project_name: Name of the project folder
        """
        project_dir = self.project_base_path / project_name
        if not project_dir.exists():
            project_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_log_file = project_dir / "execution_logs.json"
    
    def clear_logs(self) -> None:
        """Clear all logs for the current project (called at execution start)."""
        if self.current_log_file and self.current_log_file.exists():
            self.current_log_file.write_text("[]", encoding="utf-8")
    
    def add_log(self, node_id: str, message: str, level: str = "info") -> None:
        """
        Add a log entry.
        
        Args:
            node_id: ID of the node that generated the log
            message: Log message
            level: Log level (info, warning, error)
        """
        if not self.current_log_file:
            print("Warning: No active project set for logging")
            return
        
        # Load existing logs
        logs = self._load_logs()
        
        # Add new log
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "nodeId": node_id,
            "message": message,
            "level": level
        }
        
        logs.append(log_entry)
        
        # Save
        self._save_logs(logs)
    
    def get_logs(self, since_timestamp: Optional[str] = None) -> List[Dict]:
        """
        Get logs, optionally filtered by timestamp.
        
        Args:
            since_timestamp: ISO timestamp to get logs after (optional)
            
        Returns:
            List of log entries
        """
        logs = self._load_logs()
        
        if since_timestamp:
            logs = [
                log for log in logs
                if log["timestamp"] > since_timestamp
            ]
        
        return logs
    
    def _load_logs(self) -> List[Dict]:
        """Load logs from file."""
        if not self.current_log_file or not self.current_log_file.exists():
            return []
        
        try:
            with open(self.current_log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading logs: {e}")
            return []
    
    def _save_logs(self, logs: List[Dict]) -> None:
        """Save logs to file."""
        if not self.current_log_file:
            return
        
        try:
            with open(self.current_log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Error saving logs: {e}")
