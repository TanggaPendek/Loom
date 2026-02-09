import sys
import json
import asyncio
import os
from pathlib import Path
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

# Add root for imports
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from executor.engine.engine_signal import EngineSignalHub
from executor.engine.execution_manager import ExecutionManager
from executor.engine.venv_handlers import VenvManager

# Import backend modules for state and logging
try:
    sys.path.insert(0, str(ROOT_DIR / "backend" / "src"))
    from modules.engine_state_manager import EngineStateManager
    from modules.log_manager import LogManager
    HAS_BACKEND_MODULES = True
except ImportError:
    HAS_BACKEND_MODULES = False
    print("[ENGINE WARNING] Backend modules not available, state/logging disabled")

USERDATA_PATH = ROOT_DIR / "userdata"
CURRENT_PATH = USERDATA_PATH / "state.json"

def read_current():
    if not CURRENT_PATH.exists():
        return None
    try:
        with open(CURRENT_PATH, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ENGINE ERROR] Failed to read current: {e}")
        return None

async def main_async():
    if HAS_DOTENV:
        load_dotenv()

    current = read_current()
    if not current:
        print("[ENGINE] No active project found.")
        sys.exit(1)

    graph_path = Path(current["projectPath"])
    project_path = graph_path.parent
    project_id = current.get("projectId")
    
    # 1. Venv Bootstrap Phase
    bootstrap_hub = EngineSignalHub(enable_logging=False)
    venv_mgr = VenvManager(project_path, bootstrap_hub)
    
    venv_python = venv_mgr.get_python()
    current_python = Path(sys.executable)

    # 2. Handover Check
    if current_python.resolve() != venv_python.resolve():
        print(f"[ENGINE] Bootstrap: Preparing environment...")
        await venv_mgr.ensure_venv_async()
        
        print(f"[ENGINE] Handover: Restarting inside Venv...")
        sys.stdout.flush()
        os.execl(str(venv_python), str(venv_python), *sys.argv)
        return 

    # 3. Execution Phase (Inside Venv) - NOW initialize logging and state
    engine_state_mgr = None
    log_manager = None
    
    # Initialize state manager and log manager AFTER venv handover
    if HAS_BACKEND_MODULES:
        try:
            engine_state_mgr = EngineStateManager()
            log_manager = LogManager(project_base_path=USERDATA_PATH)
            
            # Set state to initializing
            engine_state_mgr.set_engine_state("initializing", project_id=project_id)
            
            # Clear logs for new run - NOW happens only once in final environment
            if project_id:
                log_manager.clear_logs(project_id)
                log_manager.append_log(project_id, "Engine starting...")
        except Exception as e:
            print(f"[ENGINE WARNING] Failed to initialize state/logging: {e}")
    
    if log_manager and project_id:
        log_manager.append_log(project_id, "Loading graph...")
    
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    signal_hub = EngineSignalHub(enable_logging=debug_mode)
    
    with graph_path.open("r", encoding="utf-8-sig") as f:
        graph = json.load(f)

    if log_manager and project_id:
        log_manager.append_log(project_id, f"Graph loaded: {len(graph.get('nodes', []))} nodes, {len(graph.get('connections', []))} connections")
    
    exec_mgr = ExecutionManager(
        nodes=None, 
        connections=graph.get("connections", []),
        signal_hub=signal_hub
    )

    if log_manager and project_id:
        log_manager.append_log(project_id, "Initializing execution manager...")
    
    await exec_mgr.initialize_async(
        nodes=graph.get("nodes", []),
        nodebank_path=os.getenv("NODEBANK_PATH", "nodebank"),
        project_path=project_path,
        log_manager=log_manager,
        project_id=project_id
    )

    # Set state to running before execution
    if engine_state_mgr:
        engine_state_mgr.set_engine_state("running", project_id=project_id)
    
    if log_manager and project_id:
        log_manager.append_log(project_id, "Executing graph...")
    
    await exec_mgr.run_async()
    
    # Execution completed successfully
    if log_manager and project_id:
        log_manager.append_log(project_id, "Execution completed successfully")
    
    if engine_state_mgr:
        engine_state_mgr.set_engine_state("idle", project_id=project_id)
    
    print("[ENGINE] Execution completed successfully")

def main():
    project_id = None
    engine_state_mgr = None
    log_manager = None
    
    try:
        # Get project_id early for error handling
        if HAS_BACKEND_MODULES:
            try:
                current = read_current()
                if current:
                    project_id = current.get("projectId")
                    engine_state_mgr = EngineStateManager()
                    log_manager = LogManager(project_base_path=USERDATA_PATH)
            except:
                pass
        
        asyncio.run(main_async())
    except KeyboardInterrupt:
        if log_manager and project_id:
            log_manager.append_log(project_id, "Execution interrupted by user")
        if engine_state_mgr:
            engine_state_mgr.set_engine_state("idle", project_id=project_id)
        print("\n[ENGINE] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        error_msg = str(e)
        
        if log_manager and project_id:
            log_manager.append_log(project_id, f"ERROR: {error_msg}")
        
        if engine_state_mgr:
            engine_state_mgr.set_engine_state(
                "error",
                project_id=project_id,
                error={"message": error_msg, "timestamp": datetime.now(timezone.utc).isoformat()}
            )
        
        print(f"\n[ENGINE ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()