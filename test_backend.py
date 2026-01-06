# test_backend.py
import time
from pathlib import Path
from backend.src.modules.signal_hub import SignalHub
from backend.src.modules.project_manager import ProjectManager
from backend.src.modules.node_manager import NodeManager
from backend.src.modules.execution_manager import ExecutionManager

# =========================
# Initialize signal hub
# =========================
signal_hub = SignalHub()

# Logging any signals to console
def log_signal(payload):
    print("[SIGNAL]", payload)

signal_hub.on("validation_error", log_signal)
signal_hub.on("file_save", log_signal)
signal_hub.on("file_loaded", log_signal)
signal_hub.on("project_init", log_signal)
signal_hub.on("project_update", log_signal)
signal_hub.on("project_delete", log_signal)
signal_hub.on("project_index_update", log_signal)
signal_hub.on("node_add", log_signal)
signal_hub.on("node_update", log_signal)
signal_hub.on("node_delete", log_signal)
signal_hub.on("execution_started", log_signal)
signal_hub.on("execution_progress", log_signal)
signal_hub.on("execution_finished", log_signal)
signal_hub.on("execution_error", log_signal)
signal_hub.on("execution_rejected", log_signal)

# =========================
# Initialize managers
# =========================
USERDATA_PATH = Path("userdata")
CUSTOM_NODE_PATH = Path("nodebank/custom")

project_manager = ProjectManager(base_path=USERDATA_PATH, signal_hub=signal_hub)
node_manager = NodeManager(base_path=CUSTOM_NODE_PATH, signal_hub=signal_hub)
execution_manager = ExecutionManager(signal_hub)

# =========================
# Test workflow
# =========================
def run_test():
    print("=== Test: Project Initialization ===")
    signal_hub.emit("project_init_request", {"projectName": "MyProject", "description": "Test project"})

    time.sleep(0.1)

    print("\n=== Test: Add Node ===")
    node_payload = {
        "nodeId": "node1",
        "name": "TestNode",
        "metadata": {"type": "custom"},
        "position": {"x": 0, "y": 0},
        "function_code": "def run(): return 123"
    }
    signal_hub.emit("node_add_request", node_payload)

    time.sleep(0.1)

    print("\n=== Test: Update Node ===")
    node_update_payload = {
        "nodeId": "node1",
        "name": "TestNodeUpdated",
        "metadata": {"type": "custom_updated"},
        "position": {"x": 10, "y": 20}
    }
    signal_hub.emit("node_update_request", node_update_payload)

    time.sleep(0.1)

    print("\n=== Test: Engine Run ===")
    signal_hub.emit("engine_run_request", {"run_id": "run1", "project": "MyProject"})

    time.sleep(0.1)

    print("\n=== Test: Engine Stop ===")
    signal_hub.emit("engine_stop_request", {"run_id": "run1"})

# =========================
# Execute test
# =========================
if __name__ == "__main__":
    run_test()
