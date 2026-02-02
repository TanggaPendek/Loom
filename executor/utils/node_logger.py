"""
Loom Node Logger Utility

This module provides simple logging functions for node scripts.
Use log_print() in your node scripts to send user-facing messages
to the frontend log panel.

Example usage in a node script:
    from executor.utils.node_logger import log_print
    
    def my_node(param1, param2):
        log_print(f"Processing {param1} and {param2}")
        result = param1 + param2
        log_print(f"Result: {result}")
        return result
"""

import json
from pathlib import Path
from datetime import datetime
import os


# Global log file path (set by executor at runtime)
_LOG_FILE_PATH = None
_CURRENT_NODE_ID = None


def init_logger(log_file_path: str, node_id: str) -> None:
    """
    Initialize the logger for the current execution.
    
    This is called by the executor, not by node scripts.
    
    Args:
        log_file_path: Path to the log file
        node_id: ID of the currently executing node
    """
    global _LOG_FILE_PATH, _CURRENT_NODE_ID
    _LOG_FILE_PATH = Path(log_file_path)
    _CURRENT_NODE_ID = node_id
    
    # Create log file if it doesn't exist
    if not _LOG_FILE_PATH.exists():
        _LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _LOG_FILE_PATH.write_text("[]", encoding="utf-8")


def log_print(message: str, level: str = "info") -> None:
    """
    Log a message that will be displayed in the frontend.
    
    This is the main function that node scripts should use.
    
    Args:
        message: Message to log
        level: Log level (info, warning, error). Default is 'info'
        
    Examples:
        log_print("Starting calculation")
        log_print("Invalid input detected", level="warning")
        log_print("Operation failed", level="error")
    """
    if not _LOG_FILE_PATH or not _CURRENT_NODE_ID:
        # Fallback to console if logger not initialized
        print(f"[{level.upper()}] {message}")
        return
    
    try:
        # Load existing logs
        logs = []
        if _LOG_FILE_PATH.exists():
            with open(_LOG_FILE_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        
        # Add new log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "nodeId": _CURRENT_NODE_ID,
            "message": str(message),
            "level": level
        }
        
        logs.append(log_entry)
        
        # Save logs
        with open(_LOG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
            
    except Exception as e:
        # Fallback to console on error
        print(f"[LOG ERROR] Failed to write log: {e}")
        print(f"[{level.upper()}] {message}")


def log_warning(message: str) -> None:
    """
    Log a warning message.
    
    Args:
        message: Warning message
    """
    log_print(message, level="warning")


def log_error(message: str) -> None:
    """
    Log an error message.
    
    Args:
        message: Error message
    """
    log_print(message, level="error")
