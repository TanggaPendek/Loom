import json
from pathlib import Path
from datetime import datetime
import os

# Global log file path
_LOG_FILE_PATH = None
_CURRENT_NODE_ID = None

def get_project_log_path():
    """
    Finds the project directory from state.json and returns a path for logs.json
    """
    # Adjust this path to where your state.json actually lives relative to this script
    # Based on your previous snippet:
    state_path = Path(__file__).parent.parent.parent / "userdata" / "state.json"
    
    if state_path.exists():
        try:
            with open(state_path, "r", encoding="utf-8-sig") as f:
                state = json.load(f)
                # Get the folder containing the savefile.json
                project_dir = Path(state["projectPath"]).parent
                return project_dir / "logs.json"
        except Exception as e:
            print(f"[Logger] Error reading state.json: {e}")
    
    # Fallback to current working directory if state.json is missing
    return Path.cwd() / "logs.json"

def init_logger(node_id: str, log_file_path: str = None) -> None:
    """
    Initialize the logger. If no path is provided, it finds the project path.
    """
    global _LOG_FILE_PATH, _CURRENT_NODE_ID
    _CURRENT_NODE_ID = node_id
    
    if log_file_path:
        _LOG_FILE_PATH = Path(log_file_path)
    else:
        _LOG_FILE_PATH = get_project_log_path()
    
    # Create log file and parent directories if they don't exist
    if not _LOG_FILE_PATH.exists():
        _LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_LOG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    
    print(f"[Logger] Initialized. Logging to: {_LOG_FILE_PATH}")

def log_print(message: str, level: str = "info") -> None:
    # ... (Rest of your log_print logic stays the same)
    if not _LOG_FILE_PATH or not _CURRENT_NODE_ID:
        print(f"[{level.upper()}] {message}")
        return

    try:
        # Load, append, and save
        with open(_LOG_FILE_PATH, "r+", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "nodeId": _CURRENT_NODE_ID,
                "message": str(message),
                "level": level
            }
            logs.append(log_entry)
            
            f.seek(0)
            json.dump(logs, f, indent=2)
            f.truncate()
    except Exception as e:
        print(f"[LOG ERROR] {e}")