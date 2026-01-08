# executor/engine/main_engine.py
import sys
import json
import asyncio
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    print("[INFO] python-dotenv not installed, using environment variables only")

# Add root for imports
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from executor.engine.engine_signal import EngineSignalHub
from executor.engine.execution_manager import ExecutionManager
from executor.engine.venv_handlers import VenvManager

# ===== Paths for current project =====
USERDATA_PATH = ROOT_DIR / "userdata"
CURRENT_PATH = USERDATA_PATH / "current.json"

def read_current():
    """Read the active project from current.json"""
    if not CURRENT_PATH.exists():
        print("[ENGINE] current.json not found")
        return None
    try:
        with open(CURRENT_PATH, "r", encoding="utf-8-sig") as f:
            return json.load(f)  # stores a single object
    except Exception as e:
        print(f"[ENGINE ERROR] Failed to read current.json: {e}")
        return None

async def main_async():
    """Main async entry point for the executor engine."""
    if HAS_DOTENV:
        load_dotenv()

    # Read current project
    current = read_current()
    if not current:
        print("[ENGINE] No active project found in current.json")
        sys.exit(1)

    graph_path = Path(current["projectPath"])
    if not graph_path.exists():
        print(f"[ENGINE] Graph file not found: {graph_path}")
        sys.exit(1)

    project_path = graph_path.parent
    nodebank_path = os.getenv("NODEBANK_PATH", "nodebank")

    # -----------------------------
    # Initialize signal hub
    # -----------------------------
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    signal_hub = EngineSignalHub(enable_logging=debug_mode)

    if debug_mode:
        # example signals for debugging
        signal_hub.on("nodeloader_started", lambda p: print(f"[SIGNAL] nodeloader_started: {p}"))
        signal_hub.on("node_loaded", lambda p: print(f"[SIGNAL] node_loaded: {p['nodeId']}"))
        signal_hub.on("varmanager_initialized", lambda p: print(f"[SIGNAL] varmanager_initialized: {p}"))
        signal_hub.on("venv_ready", lambda p: print(f"[SIGNAL] venv_ready: {p}"))
        signal_hub.on("engine_run", lambda p: print(f"[SIGNAL] engine_run: {p}"))
        signal_hub.on("engine_node_started", lambda p: print(f"[SIGNAL] node_started: {p['nodeId']}"))
        signal_hub.on("engine_node_finished", lambda p: print(f"[SIGNAL] node_finished: {p['nodeId']}"))
        signal_hub.on("engine_progress", lambda p: print(f"[SIGNAL] progress: {p}"))
        signal_hub.on("engine_stop", lambda p: print(f"[SIGNAL] engine_stop: {p}"))
        signal_hub.on("engine_error", lambda p: print(f"[SIGNAL] engine_error: {p}"))

    # -----------------------------
    # Load project JSON (graph)
    # -----------------------------
    with graph_path.open("r", encoding="utf-8-sig") as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])
    connections = graph.get("connections", [])
    
    print(f"\n[ENGINE] Running project: {current.get('projectName')}")
    print(f"[ENGINE] Nodes: {len(nodes)}, Connections: {len(connections)}")

    # -----------------------------
    # Initialize ExecutionManager
    # This handles NodeLoader, VenvManager, and VariableManager concurrently
    # -----------------------------
    exec_mgr = ExecutionManager(
        nodes=None,  # will be set during initialize_async
        connections=connections,
        signal_hub=signal_hub
    )

    print(f"\n[ENGINE] Starting async initialization...")
    await exec_mgr.initialize_async(
        nodes=nodes,
        nodebank_path=nodebank_path,
        project_path=project_path
    )

    print(f"\n[ENGINE] Initialization complete, starting execution...")
    await exec_mgr.run_async()  # runs the nodes / updates variables

    print("\n[ENGINE] Final variables:", exec_mgr.var_mgr.variables)
    print("[ENGINE] Done.")

def main():
    """Synchronous wrapper for main_async."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n[ENGINE] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ENGINE ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# main_engine.py
if __name__ == "__main__":
    print("[ENGINE] Starting engine…")
    sys.stdout.flush()  # force immediate flush so Popen reads it
    main()  # your main function
