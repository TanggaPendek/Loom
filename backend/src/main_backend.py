import sys, json, os, subprocess, uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Your Module Imports ---
from .modules.project_manager import ProjectManager
from .modules.node_manager import NodeManager
from .modules.signal_hub import SignalHub
from .modules.execution_manager import ExecutionManager
from .api_router import create_dispatcher

# ===== 1. ENV & PATHS =====
ROOT_DIR = Path(__file__).parent.parent.parent
USERDATA_PATH = ROOT_DIR / os.getenv("USERDATA_PATH", "userdata")
NODEBANK_PATH = ROOT_DIR / os.getenv("NODEBANK_PATH", "nodebank")
NODE_INDEX_PATH = NODEBANK_PATH / "nodeindex.json"

for folder in ["custom", "builtin"]:
    (NODEBANK_PATH / folder).mkdir(parents=True, exist_ok=True)
USERDATA_PATH.mkdir(parents=True, exist_ok=True)

# ===== 2. CORE SYSTEM INITIALIZATION =====
signal_hub = SignalHub()
project_backend = ProjectManager(base_path=USERDATA_PATH, signal_hub=signal_hub)
node_backend = NodeManager(base_path=NODEBANK_PATH / "custom", signal_hub=signal_hub)
execution_manager = ExecutionManager(signal_hub=signal_hub)

# ===== 3. GLOBAL HANDLERS (The Glue) =====

def handle_engine_output(payload):
    """Catches raw stdout from the engine."""
    line = payload.get("line", "")
    if line.startswith("PROGRESS:"):
        print(f"UI Update: {line}")
    else:
        print(f"Engine Log: {line}")

def on_finished(payload):
    """Handles logic when the execution stops."""
    exit_code = payload.get("exit_code")
    print(f"System: Execution stopped with code {exit_code}")

def log_signal(payload):
    if os.getenv("DEBUG", "False").lower() == "true":
        print(f"[SIGNAL] {payload}")

def launch_engine(payload):
    """Handles the manual launch if needed (ExecutionManager usually handles this too)."""
    print("[BACKEND] Launching executor engine via signal...")
    engine_path = ROOT_DIR / "executor" / "engine" / "main_engine.py"
    try:
        subprocess.Popen([sys.executable, str(engine_path)]) 
    except Exception as e:
        print(f"[BACKEND ERROR] Failed to launch engine: {e}")

# ===== 4. REGISTER SIGNAL LISTENERS (No Decorators) =====

# General logging
events = [
    "project_init", "project_update", "project_delete", "project_index_update",
    "node_add", "node_update", "node_delete", "file_save", "file_loaded",
    "execution_started", "execution_progress", "execution_finished", "execution_error"
]
for event in events:
    signal_hub.on(event, log_signal)

# Specific Logic Wiring
signal_hub.on("execution_output", handle_engine_output)
signal_hub.on("execution_finished", on_finished)
# Note: ExecutionManager already listens for engine_run_request, 
# but if you want this extra log, keep the line below:
signal_hub.on("engine_run_request", launch_engine)

# ===== 5. STARTUP PAYLOAD LOGIC =====
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
            with open(path, "r", encoding="utf-8-sig") as f:
                result[key] = json.load(f)
        else:
            result[key] = None
    return result

# ===== 6. WEB SERVER (FASTAPI) =====
app = FastAPI(title="Loom Offline Backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/startup")
async def startup():
    return get_startup_payload()

# Attach the Single-URL Dispatcher
app.include_router(create_dispatcher(signal_hub, project_backend))

if __name__ == "__main__":
    print(f"Loom Backend active at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)