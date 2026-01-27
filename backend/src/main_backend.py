import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import USERDATA_PATH, NODEBANK_PATH, init_directories
from .handlers import (
    log_signal, handle_engine_output, on_finished, 
    launch_engine, get_startup_payload, handle_load_graph, project_load_request,graph_node_add, graph_node_delete,
)

# Core Module Imports
from .modules.project_manager import ProjectManager
from .modules.node_manager import NodeManager
from .modules.signal_hub import SignalHub
from .modules.execution_manager import ExecutionManager
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
index_service = IndexService(
    project_base=USERDATA_PATH,
    node_bank_path=NODEBANK_PATH,
    signal_hub=signal_hub
)
signal_hub.on("load_graph_request", handle_load_graph)
signal_hub.on("startup_request", handle_startup_request)
signal_hub.on("load_graph_request", handle_load_graph)
signal_hub.on("project_load_request", project_load_request)
signal_hub.on("project_node_add", graph_node_add)
signal_hub.on("project_node_delete", graph_node_delete)

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
signal_hub.on("engine_run_request", launch_engine)

# 4. Web Server Setup
app = FastAPI(title="Loom Offline Backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


app.include_router(create_dispatcher(signal_hub, project_backend))

if __name__ == "__main__":
    print(f"Loom Backend active at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)