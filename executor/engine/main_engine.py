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

# Add root for imports
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from executor.engine.engine_signal import EngineSignalHub
from executor.engine.execution_manager import ExecutionManager
from executor.engine.venv_handlers import VenvManager

USERDATA_PATH = ROOT_DIR / "userdata"
CURRENT_PATH = USERDATA_PATH / "current.json"

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

    # 3. Execution Phase (Inside Venv)
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    signal_hub = EngineSignalHub(enable_logging=debug_mode)
    
    with graph_path.open("r", encoding="utf-8-sig") as f:
        graph = json.load(f)

    exec_mgr = ExecutionManager(
        nodes=None, 
        connections=graph.get("connections", []),
        signal_hub=signal_hub
    )

    await exec_mgr.initialize_async(
        nodes=graph.get("nodes", []),
        nodebank_path=os.getenv("NODEBANK_PATH", "nodebank"),
        project_path=project_path
    )

    await exec_mgr.run_async()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"\n[ENGINE ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()