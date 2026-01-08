import sys
import json
import os
import subprocess
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[INFO] python-dotenv not installed, using environment variables only")

from .modules.project_manager import ProjectManager
from .modules.node_manager import NodeManager
from .modules.signal_hub import SignalHub
from .modules.execution_manager import ExecutionManager

# ===== Paths =====
ROOT_DIR = Path(__file__).parent.parent.parent
NODEBANK_PATH = ROOT_DIR / os.getenv("NODEBANK_PATH", "nodebank")
CUSTOM_NODE_PATH = ROOT_DIR / os.getenv("CUSTOM_NODE_PATH", "nodebank/custom")
BUILTIN_NODE_PATH = ROOT_DIR / os.getenv("BUILTIN_NODE_PATH", "nodebank/builtin")
USERDATA_PATH = ROOT_DIR / os.getenv("USERDATA_PATH", "userdata")
NODE_INDEX_PATH = NODEBANK_PATH / "nodeindex.json"

# Ensure folders exist
CUSTOM_NODE_PATH.mkdir(parents=True, exist_ok=True)
BUILTIN_NODE_PATH.mkdir(parents=True, exist_ok=True)
USERDATA_PATH.mkdir(parents=True, exist_ok=True)

# ===== Signal Hub =====
signal_hub = SignalHub()

# ===== Managers =====
project_backend = ProjectManager(base_path=USERDATA_PATH, signal_hub=signal_hub)
node_backend = NodeManager(base_path=CUSTOM_NODE_PATH, signal_hub=signal_hub)
execution_manager = ExecutionManager(signal_hub=signal_hub)

# ===== Logging listener =====
def log_signal(payload):
    if os.getenv("DEBUG", "False").lower() == "true":
        print(f"[SIGNAL] {payload}")

for event in [
    "project_init", "project_update", "project_delete", "project_index_update",
    "node_add", "node_update", "node_delete", "file_save", "file_loaded",
    "execution_started", "execution_progress", "execution_finished", "execution_error"
]:
    signal_hub.on(event, log_signal)

# ===== Helper =====
def load_payload(payload_arg):
    path = Path(payload_arg)
    if path.is_file():
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return json.loads(payload_arg)

# ===== Main dispatcher =====
def main():
    if len(sys.argv) < 2:
        print("Usage: python -m backend.src.main_backend <command> [args]")
        sys.exit(1)

    command = sys.argv[1].lower()
    payload = None

    
    if command in ["run", "stop"]:
        # For run/stop, default to current.json
        current_file = USERDATA_PATH / "current.json"
        if current_file.exists():
            with open(current_file, "r", encoding="utf-8-sig") as f:
                payload = json.load(f)
        else:
            print(f"[ERROR] current.json not found for {command}")
            sys.exit(1)
    else:
        if len(sys.argv) < 3:
            print(f"{command} requires payload or project/node name")
            sys.exit(1)
        if command in ["init", "addnode", "updatenode", "save"]:
            payload = load_payload(sys.argv[2])
        else:
            payload = {"name": sys.argv[2]}


    # Emit signals
    mapping = {
        "init": "project_init_request",
        "save": "project_update_request",
        "delete": "project_delete_request",
        "addnode": "node_add_request",
        "updatenode": "node_update_request",
        "deletenode": "node_delete_request",
        "run": "engine_run_request",
        "stop": "engine_stop_request"
    }

    signal_name = mapping.get(command, "")
    if signal_name:
        signal_hub.emit(signal_name, payload)
    
    # If run command, also launch the executor engine
    if command == "run":
        print("[BACKEND] Launching executor engine...")
        engine_path = ROOT_DIR / "executor" / "engine" / "main_engine.py"
        try:
            result = subprocess.run(
                [sys.executable, str(engine_path)],
                capture_output=False,
                text=True
            )
            if result.returncode != 0:
                print(f"[BACKEND] Engine execution failed with code {result.returncode}")
        except Exception as e:
            print(f"[BACKEND ERROR] Failed to launch engine: {e}")

# ===== Startup API =====
def startup_payload():
    files = {
        "setting": USERDATA_PATH / "setting.json",
        "current": USERDATA_PATH / "current.json",
        "project_index": USERDATA_PATH / "projectindex.json",
        "node_index": NODE_INDEX_PATH  # already points to NODEBANK_PATH / "nodeindex.json"
    }

    result = {}
    for key, path in files.items():
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    result[key] = json.load(f)
            except Exception as e:
                result[key] = {"error": str(e)}
        else:
            result[key] = None  # file does not exist

    return result


if __name__ == "__main__":
    main()
