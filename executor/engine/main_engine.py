import sys
import json
import asyncio
import os
import subprocess
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


def launch_ws_service() -> subprocess.Popen:
    """Start ws_service.py as a background subprocess."""
    script = str(ROOT_DIR / "executor" / "engine" / "ws_service.py")
    proc = subprocess.Popen(
        [sys.executable, script],
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=os.environ.copy(),
    )
    print(f"[ENGINE] WS service started (pid={proc.pid})")
    sys.stdout.flush()
    return proc


async def main_async(ws_service_proc=None):
    if HAS_DOTENV:
        load_dotenv()

    current = read_current()
    if not current:
        print("[ENGINE] No active project found.")
        sys.exit(1)

    graph_path = Path(current["projectPath"])
    project_path = graph_path.parent
    project_id = current.get("projectId")

    # --- WS client setup (inside venv — after handover) ---
    from executor.engine.ws_client import EngineWSClient, set_client
    ws_client = EngineWSClient()
    await ws_client.connect()
    set_client(ws_client)

    # --- INIT broadcast ---
    print("[ENGINE] Initializing...")
    sys.stdout.flush()
    await ws_client.send("engine_start", {"projectId": project_id})

    # 1. Venv/handover DISABLED — run directly in the current interpreter.
    # Install project requirements inline if they exist.
    req_file = project_path / "requirements.txt"
    if req_file.exists():
        print(f"[ENGINE] Installing project deps...")
        sys.stdout.flush()
        import subprocess as _sp
        _sp.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            check=False, capture_output=True
        )
        print("[ENGINE] Deps ready.")
        sys.stdout.flush()


    # 3. Execution Phase (Inside Venv)
    engine_state_mgr = None
    log_manager = None

    if HAS_BACKEND_MODULES:
        try:
            engine_state_mgr = EngineStateManager()
            log_manager = LogManager(project_base_path=USERDATA_PATH)
            engine_state_mgr.set_engine_state("initializing", project_id=project_id)
            if project_id:
                log_manager.clear_logs(project_id)
        except Exception as e:
            print(f"[ENGINE WARNING] Failed to initialize state/logging: {e}")

    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    signal_hub = EngineSignalHub(enable_logging=debug_mode)

    with graph_path.open("r", encoding="utf-8-sig") as f:
        graph = json.load(f)

    exec_mgr = ExecutionManager(
        nodes=None,
        connections=graph.get("connections", []),
        signal_hub=signal_hub,
        ws_client=ws_client,
    )

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

    print("[ENGINE] Running graph...")
    sys.stdout.flush()
    await exec_mgr.run_async()

    # Execution completed successfully
    if engine_state_mgr:
        engine_state_mgr.set_engine_state("idle", project_id=project_id)

    print("[ENGINE] Execution completed successfully")
    sys.stdout.flush()
    await ws_client.send("engine_finish", {})
    await ws_client.close()


def main():
    project_id = None
    engine_state_mgr = None
    log_manager = None
    ws_service_proc = None

    # --ws-running is injected into argv after venv handover so we skip re-launching ws_service
    ws_already_running = "--ws-running" in sys.argv
    if ws_already_running:
        sys.argv.remove("--ws-running")
    else:
        # Launch WS service only on first invocation (before venv handover)
        ws_service_proc = launch_ws_service()
        import time
        time.sleep(1.0)  # Give ws_service time to start

    try:
        if HAS_BACKEND_MODULES:
            try:
                current = read_current()
                if current:
                    project_id = current.get("projectId")
                    engine_state_mgr = EngineStateManager()
                    log_manager = LogManager(project_base_path=USERDATA_PATH)
            except:
                pass

        asyncio.run(main_async(ws_service_proc=ws_service_proc))
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
        # Try to broadcast error
        try:
            import asyncio as _asyncio
            from executor.engine.ws_client import get_client
            cli = get_client()
            if cli:
                _asyncio.run(cli.send("engine_error", {"message": error_msg}))
                _asyncio.run(cli.close())
        except Exception:
            pass
        sys.exit(1)
    finally:
        if ws_service_proc and ws_service_proc.poll() is None:
            ws_service_proc.terminate()
            print("[ENGINE] WS service stopped")



if __name__ == "__main__":
    main()