import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from .modules.project_manager import ProjectManager
from .modules.node_manager import NodeManager
from .modules.signal_hub import SignalHub

# Load environment variables
load_dotenv()

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

# ===== Example logging listener =====
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
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(payload_arg)

# ===== Main dispatcher =====
def main():
    if len(sys.argv) < 2:
        print("Usage: python -m backend.src.main_backend <command> [args]")
        sys.exit(1)

    command = sys.argv[1].lower()
    payload = None

    if command in ["init", "save", "delete", "addnode", "updatenode", "deletenode"]:
        if len(sys.argv) < 3:
            print(f"{command} requires payload or project/node name")
            sys.exit(1)
        if command in ["init", "addnode", "updatenode", "save"]:
            payload = load_payload(sys.argv[2])
        else:
            payload = {"name": sys.argv[2]}

    # ===== Emit signals instead of direct calls =====
    if command == "init":
        signal_hub.emit("project_init_request", payload)

    elif command == "save":
        signal_hub.emit("project_update_request", payload)

    elif command == "delete":
        signal_hub.emit("project_delete_request", payload)

    elif command == "addnode":
        signal_hub.emit("node_add_request", payload)

    elif command == "updatenode":
        signal_hub.emit("node_update_request", payload)

    elif command == "deletenode":
        signal_hub.emit("node_delete_request", payload)

    elif command == "index":
        signal_hub.emit("project_index_request", payload)

    elif command == "nodeindex":
        signal_hub.emit("node_index_request", payload)

    elif command == "run":
        signal_hub.emit("engine_run_request", payload)

    elif command == "stop":
        signal_hub.emit("engine_stop_request", payload)

    else:
        print(f"Unknown command '{command}'")


if __name__ == "__main__":
    main()
