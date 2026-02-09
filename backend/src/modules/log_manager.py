"""
Loom Log Manager

Manages execution logs for displaying in the frontend UI.
Logs are stored per-project in logs.json files.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional


class LogManager:
    """
    Manages execution logs for frontend display.
    
    Logs are stored per-project in {project}/logs.json and cleared on each execution start.
    """
    
    def __init__(self, project_base_path: Path):
        """
        Initialize LogManager.
        
        Args:
            project_base_path: Base path for userdata (where projects are stored)
        """
        self.project_base_path = Path(project_base_path)
        self.state_file = self.project_base_path / "state.json"
    
    def _get_project_name(self, project_id: str) -> Optional[str]:
        """
        Get project name from state.json.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project name or None if not found
        """
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                # Check if this is the active project
                if state.get("projectId") == project_id:
                    return state.get("projectName")
        except:
            pass
        
        return None
    
    def _get_log_file(self, project_id: str) -> Optional[Path]:
        """Get path to log file for a project."""
        project_name = self._get_project_name(project_id)
        if project_name:
            project_folder = self.project_base_path / project_name
            if project_folder.exists():
                return project_folder / "logs.json"
        return None
    
    def clear_logs(self, project_id: str) -> None:
        """
        Clear all logs for the specified project.
        
        Args:
            project_id: Project ID
        """
        log_file = self._get_log_file(project_id)
        if log_file:
            try:
                log_file.write_text("[]", encoding="utf-8")
                print(f"[LogManager] Cleared logs: {log_file}")
            except Exception as e:
                print(f"[LogManager ERROR] Failed to clear logs: {e}")
        else:
            print(f"[LogManager WARNING] Could not find log file for project {project_id}")
    
    def append_log(self, project_id: str, message: str, level: str = "info") -> None:
        """
        Append a log entry for the specified project.
        
        Args:
            project_id: Project ID
            message: Log message
            level: Log level (info, warning, error)
        """
        log_file = self._get_log_file(project_id)
        if not log_file:
            print(f"[LogManager WARNING] Could not find log file for project {project_id}")
            return
        
        # Load existing logs
        logs = []
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except:
                logs = []
        
        # Add new log entry
        log_entry = {
            "time": datetime.now(timezone.utc).isoformat(),
            "msg": message,
            "level": level
        }
        
        logs.append(log_entry)
        
        # Save logs
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"[LogManager ERROR] Failed to save logs: {e}")
    
    def get_logs(self, project_id: str) -> List[Dict]:
        """
        Get all logs for the specified project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of log entries
        """
        log_file = self._get_log_file(project_id)
        if not log_file or not log_file.exists():
            return []
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[LogManager ERROR] Failed to load logs: {e}")
            return []
