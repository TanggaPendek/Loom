import shutil
import json
from pathlib import Path
from .storage_manager import StorageManager

class VenvCleaner:
    @staticmethod
    def run_fifo_clean(project_id: str, project_path_str: str):
        """
        Triggered before execution. 
        Deletes the oldest venv if history > limit, then adds current project to history.
        """
        state = StorageManager.get_state()
        settings = StorageManager.get_settings()
        
        limit = settings.get("max_venv_count", 3)
        history = state.get("history", [])

        # 1. Remove if exists to move to end of FIFO (freshest)
        history = [p for p in history if p["projectId"] != project_id]

        # 2. Check limit
        if len(history) >= limit:
            # Pop oldest (index 0)
            oldest = history.pop(0)
            # projectPath is 'userdata/folder/file.json', venv is 'userdata/folder/venv'
            oldest_dir = Path(oldest["projectPath"]).parent
            venv_to_del = oldest_dir / "venv"
            
            if venv_to_del.exists() and venv_to_del.is_dir():
                print(f"[CLEANER] FIFO: Deleting oldest venv at {venv_to_del}")
                shutil.rmtree(venv_to_del, ignore_errors=True)

        # 3. Add current project to history
        history.append({
            "projectId": project_id,
            "projectPath": project_path_str
        })

        # 4. Save state
        state["history"] = history
        StorageManager.save_state(state)

    @staticmethod
    def clean_all_venvs() -> int:
        """
        Full Wipe: Deletes all 'venv' folders in userdata and clears history.
        """
        base_path = StorageManager.USERDATA_DIR
        # glob find all folders named venv
        venvs_found = list(base_path.glob("**/venv"))
        
        count = 0
        for venv_path in venvs_found:
            if venv_path.is_dir():
                print(f"[CLEANER] Nuclear: Removing {venv_path}")
                shutil.rmtree(venv_path, ignore_errors=True)
                count += 1
        
        # Reset history in state
        state = StorageManager.get_state()
        state["history"] = []
        StorageManager.save_state(state)
        
        return count