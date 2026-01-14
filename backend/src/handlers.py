import sys
import json
import os
import subprocess
from .config import ROOT_DIR, USERDATA_PATH, NODE_INDEX_PATH


PROJECT_INDEX_PATH = USERDATA_PATH / "projectindex.json"
STATE_PATH = USERDATA_PATH / "state.json"


def handle_engine_output(payload):
    line = payload.get("line", "")
    if line.startswith("PROGRESS:"):
        print(f"UI Update: {line}")
    else:
        print(f"Engine Log: {line}")

def on_finished(payload):
    exit_code = payload.get("exit_code")
    print(f"System: Execution stopped with code {exit_code}")

def log_signal(payload):
    if os.getenv("DEBUG", "False").lower() == "true":
        print(f"[SIGNAL] {payload}")

def launch_engine(payload):
    print("[BACKEND] Launching executor engine via signal...")
    engine_path = ROOT_DIR / "executor" / "engine" / "main_engine.py"
    try:
        subprocess.Popen([sys.executable, str(engine_path)]) 
    except Exception as e:
        print(f"[BACKEND ERROR] Failed to launch engine: {e}")

def get_startup_payload():
    files = {
        "setting": USERDATA_PATH / "setting.json",
        "current": USERDATA_PATH / "current.json",
        "project_index": USERDATA_PATH / "projectindex.json",
        "node_index": NODE_INDEX_PATH
    }
    result = {}
    for key, path in files.items():
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    result[key] = json.load(f)
            except Exception as e:
                print(f"Error reading {key}: {e}")
                result[key] = None
        else:
            result[key] = None
    return result

# handlers.py

def handle_load_graph(payload=None):
    """Dynamically loads graph based on state.json"""
    state_path = USERDATA_PATH / "state.json"
    
    if not state_path.exists():
        return {"status": "error", "message": "state.json missing"}

    try:
        with open(state_path, "r", encoding="utf-8-sig") as f:
            state_data = json.load(f)
        
        project_path_str = state_data.get("projectPath")
        if not project_path_str:
            return {"status": "error", "message": "No projectPath in state"}

        from pathlib import Path
        graph_path = Path(project_path_str)

        if graph_path.exists():
            with open(graph_path, "r", encoding="utf-8-sig") as f:
                graph_content = json.load(f)
            
            return {
                "metadata": state_data,
                "graph": graph_content
            }
        return {"status": "error", "message": "Graph file not found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def project_load_request(payload):
    print("handle_select_project called with:", payload)
    try:
        project_id = payload.get("projectId")
        print("project_id:", project_id)

        if not PROJECT_INDEX_PATH.exists():
            raise FileNotFoundError(f"{PROJECT_INDEX_PATH} missing")

        with open(PROJECT_INDEX_PATH, "r", encoding="utf-8") as f:
            project_index = json.load(f)
        print("project_index loaded:", project_index)

        project = next((p for p in project_index if p.get("projectId") == project_id), None)
        if not project:
            raise ValueError(f"Project '{project_id}' not found")

        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=4)
        print("STATE_PATH updated successfully")

        return {"status": "ok", "projectId": project_id}

    except Exception as e:
        print("ERROR in handle_select_project:", e)
        return {"status": "error", "message": str(e)}
