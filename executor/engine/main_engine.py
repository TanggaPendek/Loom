# executor/engine/main_engine.py
import sys
import json
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Add root to path for imports
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from executor.engine.engine_signal import EngineSignalHub
from executor.engine.execution_manager import ExecutionManager


async def main_async():
    """Main async entry point for the executor engine."""
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: python -m executor.engine.main_engine <graph.json>")
        sys.exit(1)

    graph_path = Path(sys.argv[1])
    if not graph_path.exists():
        print(f"[ERROR] Graph file not found: {graph_path}")
        sys.exit(1)

    with graph_path.open("r", encoding="utf-8") as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])
    connections = graph.get("connections", [])
    nodebank_path = os.getenv("NODEBANK_PATH", "nodebank")
    project_path = graph_path.parent  # Project path is where the graph.json is

    # Create signal hub with logging enabled in debug mode
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    signal_hub = EngineSignalHub(enable_logging=debug_mode)

    # Register signal listeners for logging
    if debug_mode:
        signal_hub.on("nodeloader_started", lambda p: print(f"[SIGNAL] nodeloader_started: {p}"))
        signal_hub.on("node_loaded", lambda p: print(f"[SIGNAL] node_loaded: {p['nodeId']}"))
        signal_hub.on("nodeloader_completed", lambda p: print(f"[SIGNAL] nodeloader_completed: {p}"))
        
        signal_hub.on("varmanager_started", lambda p: print(f"[SIGNAL] varmanager_started"))
        signal_hub.on("varmanager_initialized", lambda p: print(f"[SIGNAL] varmanager_initialized: {p}"))
        
        signal_hub.on("venv_ready", lambda p: print(f"[SIGNAL] venv_ready"))
        
        signal_hub.on("engine_run", lambda p: print(f"[SIGNAL] engine_run: {p}"))
        signal_hub.on("engine_node_started", lambda p: print(f"[SIGNAL] node_started: {p['nodeId']}"))
        signal_hub.on("engine_node_finished", lambda p: print(f"[SIGNAL] node_finished: {p['nodeId']}"))
        signal_hub.on("engine_progress", lambda p: print(f"[SIGNAL] progress: {p}"))
        signal_hub.on("engine_stop", lambda p: print(f"[SIGNAL] engine_stop: {p}"))
        signal_hub.on("engine_error", lambda p: print(f"[SIGNAL] engine_error: {p}"))

    # Create execution manager
    exec_mgr = ExecutionManager(
        nodes=None,  # Will be set by initialize_async
        connections=connections,
        signal_hub=signal_hub
    )

    print(f"\n[ENGINE] Starting async initialization...")
    print(f"[ENGINE] Nodes: {len(nodes)}, Connections: {len(connections)}")
    
    # Initialize components concurrently (NodeLoader, VenvManager, VariableManager)
    await exec_mgr.initialize_async(
        nodes=nodes,
        nodebank_path=nodebank_path,
        project_path=project_path
    )

    print(f"\n[ENGINE] Initialization complete, starting execution...")
    
    # Run execution asynchronously
    await exec_mgr.run_async()

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


if __name__ == "__main__":
    main()
