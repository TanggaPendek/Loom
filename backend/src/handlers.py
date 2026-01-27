import sys
import json
import os
import subprocess
from .config import ROOT_DIR, USERDATA_PATH, NODE_INDEX_PATH
from pathlib import Path
from datetime import datetime



PROJECT_INDEX_PATH = USERDATA_PATH / "projectindex.json"
STATE_PATH = USERDATA_PATH / "state.json"
NODE_INDEX_PATH = ROOT_DIR / "nodebank" / "nodeindex.json"


def handle_engine_output(payload):
    line = payload.get("line", "")
    if line.startswith("PROGRESS:"):
        print(f"UI Update: {line}")
    else:
        print(f"Engine Log: {line}")

def on_finished(payload):
    exit_code = payload.get("exit_code")
    print(f"System: Execution stopped with code {exit_code}")

def log_signal(payload):
    if os.getenv("DEBUG", "False").lower() == "true":
        print(f"[SIGNAL] {payload}")

def launch_engine(payload):
    print("[BACKEND] Launching executor engine via signal...")
    engine_path = ROOT_DIR / "executor" / "engine" / "main_engine.py"
    try:
        subprocess.Popen([sys.executable, str(engine_path)]) 
    except Exception as e:
        print(f"[BACKEND ERROR] Failed to launch engine: {e}")

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
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    result[key] = json.load(f)
            except Exception as e:
                print(f"Error reading {key}: {e}")
                result[key] = None
        else:
            result[key] = None
    return result

# handlers.py

def handle_load_graph(payload=None):
    """Dynamically loads graph based on state.json"""
    state_path = USERDATA_PATH / "state.json"
    
    if not state_path.exists():
        return {"status": "error", "message": "state.json missing"}

    try:
        with open(state_path, "r", encoding="utf-8-sig") as f:
            state_data = json.load(f)
        
        project_path_str = state_data.get("projectPath")
        if not project_path_str:
            return {"status": "error", "message": "No projectPath in state"}

        from pathlib import Path
        graph_path = Path(project_path_str)

        if graph_path.exists():
            with open(graph_path, "r", encoding="utf-8-sig") as f:
                graph_content = json.load(f)
            
            return {
                "metadata": state_data,
                "graph": graph_content
            }
        return {"status": "error", "message": "Graph file not found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def project_load_request(payload):
    print("handle_select_project called with:", payload)
    try:
        project_id = payload.get("projectId")
        print("project_id:", project_id)

        if not PROJECT_INDEX_PATH.exists():
            raise FileNotFoundError(f"{PROJECT_INDEX_PATH} missing")

        with open(PROJECT_INDEX_PATH, "r", encoding="utf-8") as f:
            project_index = json.load(f)
        print("project_index loaded:", project_index)

        project = next((p for p in project_index if p.get("projectId") == project_id), None)
        if not project:
            raise ValueError(f"Project '{project_id}' not found")

        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=4)
        print("STATE_PATH updated successfully")

        return {"status": "ok", "projectId": project_id}

    except Exception as e:
        print("ERROR in handle_select_project:", e)
        return {"status": "error", "message": str(e)}

def graph_node_add(payload):
    """Adds a node dynamically using frontend payload and node index from nodeindex.json"""
    try:
        if not STATE_PATH.exists():
            return {"status": "error", "message": "state.json missing"}

        with open(STATE_PATH, "r", encoding="utf-8-sig") as f:
            state_data = json.load(f)

        project_path_str = state_data.get("projectPath")
        if not project_path_str:
            return {"status": "error", "message": "No projectPath in state"}

        project_path = Path(project_path_str)
        if not project_path.exists():
            return {"status": "error", "message": "Project file not found"}

        # --- Load graph ---
        with open(project_path, "r", encoding="utf-8-sig") as f:
            graph_content = json.load(f)

        nodes = graph_content.get("nodes", [])
        node_count = len(nodes) + 1
        node_id = f"node_{node_count}"
        position_id = f"pos_{node_count}"

     
        if not NODE_INDEX_PATH.exists():
            return {"status": "error", "message": "Node index not found"}

        with open(NODE_INDEX_PATH, "r", encoding="utf-8-sig") as f:
            node_index = json.load(f)

        # --- Find template by payload type ---
        node_type_name = payload.get("type")
        if not node_type_name:
            return {"status": "error", "message": "No node type provided"}

        template = next((n for n in node_index if n["name"].lower() == node_type_name.lower()), None)
        if not template:
            return {"status": "error", "message": f"Node type '{node_type_name}' not found in node index"}

        # --- Dynamic inputs/outputs ---
        dynamic_inputs = [{"var": inp} for inp in template.get("dynamic", {}).get("inputs", [])]
        dynamic_outputs = template.get("dynamic", {}).get("outputs", [])

        # --- Position ---
        pos_x = payload.get("x", 100 * node_count)
        pos_y = payload.get("y", 100)

        new_node = {
            "nodeId": node_id,
            "positionId": position_id,
            "name": f"{template['name'].lower()}_node",
            "position": {"x": pos_x, "y": pos_y},
            "input": dynamic_inputs,
            "output": dynamic_outputs,
            "ref": template.get("type", "builtin"),
            "scriptPath": template.get("scriptPath"),
            "entryFunction": template.get("entryFunction"),
            "metadata": {"operation": template['name'].lower()}
        }

        nodes.append(new_node)
        graph_content["nodes"] = nodes

        with open(project_path, "w", encoding="utf-8") as f:
            json.dump(graph_content, f, indent=4)

        return {"status": "ok", "node": new_node}

    except Exception as e:
        print("ERROR in graph_node_add:", e)
        return {"status": "error", "message": str(e)}
    
def graph_node_delete(payload):
    """Removes a node and its associated edges from the project JSON."""
    try:
        if not STATE_PATH.exists():
            return {"status": "error", "message": "state.json missing"}

        with open(STATE_PATH, "r", encoding="utf-8-sig") as f:
            state_data = json.load(f)

        project_path_str = state_data.get("projectPath")
        if not project_path_str:
            return {"status": "error", "message": "No projectPath in state"}

        project_path = Path(project_path_str)
        if not project_path.exists():
            return {"status": "error", "message": "Project file not found"}

        # --- Load graph ---
        with open(project_path, "r", encoding="utf-8-sig") as f:
            graph_content = json.load(f)

        target_id = payload.get("nodeId")
        if not target_id:
            return {"status": "error", "message": "No nodeId provided in payload"}

        # --- Remove the Node ---
        original_node_count = len(graph_content.get("nodes", []))
        graph_content["nodes"] = [
            n for n in graph_content.get("nodes", []) 
            if n.get("nodeId") != target_id
        ]

        if len(graph_content["nodes"]) == original_node_count:
            return {"status": "error", "message": f"Node '{target_id}' not found"}

        # --- Clean up Edges (Unraveling the threads) ---
        # We remove any edge where the target_id is either the source or the target
        if "edges" in graph_content:
            graph_content["edges"] = [
                e for e in graph_content.get("edges", [])
                if e.get("source") != target_id and e.get("target") != target_id
            ]

        # --- Save ---
        with open(project_path, "w", encoding="utf-8") as f:
            json.dump(graph_content, f, indent=4)

        return {"status": "ok", "deletedNodeId": target_id}

    except Exception as e:
        print("ERROR in graph_node_delete:", e)
        return {"status": "error", "message": str(e)}
