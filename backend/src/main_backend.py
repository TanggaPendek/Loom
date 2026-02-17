from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import USERDATA_PATH, NODEBANK_PATH, init_directories
from .handlers import (
    log_signal, handle_engine_output, on_finished, 
    launch_engine, get_startup_payload, handle_load_graph, project_load_request,
    graph_node_add, graph_node_delete, connection_create, connection_delete,
    graph_node_update_input, graph_node_move,
    handle_engine_state_request, handle_engine_logs_request,
)

# Core Module Imports
from .modules.project_manager import ProjectManager
from .modules.node_manager import NodeManager
from .modules.signal_hub import SignalHub
from .modules.execution_manager import ExecutionManager
from .modules.log_manager import LogManager
from .api_router import create_dispatcher
from .modules.index_service import IndexService



# 1. Initialize Folders
init_directories()

def handle_startup_request(payload):
    signal_hub.emit_concurrent("hot_reload_all")
    return get_startup_payload()

# 2. Initialize Core Systems
signal_hub = SignalHub()
project_backend = ProjectManager(base_path=USERDATA_PATH, signal_hub=signal_hub)
node_backend = NodeManager(base_path=NODEBANK_PATH / "custom", signal_hub=signal_hub)
execution_manager = ExecutionManager(signal_hub=signal_hub)
log_manager = LogManager(project_base_path=USERDATA_PATH)
index_service = IndexService(
    project_base=USERDATA_PATH,
    node_bank_path=NODEBANK_PATH,
    signal_hub=signal_hub
)
signal_hub.on("load_graph_request", handle_load_graph)
signal_hub.on("startup_request", handle_startup_request)
signal_hub.on("project_load_request", project_load_request)
signal_hub.on("project_node_add", graph_node_add)
signal_hub.on("project_node_delete", graph_node_delete)
signal_hub.on("connection_create_request", connection_create)
signal_hub.on("connection_delete_request", connection_delete)
signal_hub.on("graph_node_update_input_request", graph_node_update_input)
signal_hub.on("graph_node_move_request", graph_node_move)
signal_hub.on("project_delete_request", lambda p: project_backend.delete_project(
    p.get("projectId", {}).get("projectName")
))

# 3. Register Signal Listeners
events = [
    "project_init", "project_update", "project_delete", "project_index_update",
    "node_add", "node_update", "node_delete", "file_save", "file_loaded",
    "execution_started", "execution_progress", "execution_finished", "execution_error"
]
for event in events:
    signal_hub.on(event, log_signal)

signal_hub.on("execution_output", handle_engine_output)
signal_hub.on("execution_finished", on_finished)
signal_hub.on("engine_state_request", handle_engine_state_request)
signal_hub.on("engine_logs_request", handle_engine_logs_request)

# 4. Web Server Setup
# 4. Web Server Setup
app = FastAPI(title="Loom")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 1. API ROUTES FIRST
# Include your router before mounting static files
app.include_router(create_dispatcher(signal_hub, project_backend, log_manager))

# Determine Paths
if getattr(sys, "frozen", False):
    PROJECT_ROOT = sys._MEIPASS
else:
    PROJECT_ROOT = os.getcwd()

FRONTEND_DIST_PATH = os.path.join(PROJECT_ROOT, "frontend", "dist")
ASSETS_PATH = os.path.join(FRONTEND_DIST_PATH, "assets")

# 2. MOUNT SPECIFIC ASSETS FOLDER
# This ensures /assets/main.js etc. are found correctly
if os.path.exists(ASSETS_PATH):
    app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="assets")

# 3. CATCH-ALL FOR REACT/SPA
# This handles the root "/" AND any sub-paths (like /settings) 
# by serving the index.html so React can take over.
@app.get("/{catchall:path}")
def serve_react(catchall: str):
    index_path = os.path.join(FRONTEND_DIST_PATH, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend build not found. Check FRONTEND_DIST_PATH."}



app.include_router(create_dispatcher(signal_hub, project_backend, log_manager))

if __name__ == "__main__":
    print(f"Loom Backend active at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)