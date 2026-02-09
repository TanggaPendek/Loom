import json
from pathlib import Path
from typing import Dict, Any

class StorageManager:
    """Handles global engine limits and state tracking."""
    # Adjusting root to find 'userdata' relative to this script
    BASE_DIR = Path(__file__).parent.parent.parent.parent
    USERDATA_DIR = BASE_DIR / "userdata"
    SETTINGS_PATH = USERDATA_DIR / "settings.json"
    STATE_PATH = USERDATA_DIR / "state.json"

    @staticmethod
    def init_storage():
        StorageManager.USERDATA_DIR.mkdir(parents=True, exist_ok=True)
        
        if not StorageManager.SETTINGS_PATH.exists():
            defaults = {
                "max_venv_count": 3,
                "auto_clean": True
            }
            StorageManager.save_settings(defaults)

        if not StorageManager.STATE_PATH.exists():
            # state.json IS the active project data (no nesting)
            # Initialize with empty/null project
            initial_state = {
                "projectId": None,
                "projectName": None,
                "projectPath": None
            }
            StorageManager.save_state(initial_state)

    @staticmethod
    def get_settings() -> Dict[str, Any]:
        StorageManager.init_storage()
        with open(StorageManager.SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_settings(data: Dict[str, Any]):
        with open(StorageManager.SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def get_state() -> Dict[str, Any]:
        StorageManager.init_storage()
        with open(StorageManager.STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_state(data: Dict[str, Any]):
        with open(StorageManager.STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)