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

import re

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

        # --- FIX: Predictable Numbering (Check highest existing ID) ---
        max_id = 0
        for n in nodes:
            # Extract number from "node_X"
            match = re.search(r'node_(\d+)', n.get("nodeId", "0"))
            if match:
                num = int(match.group(1))
                if num > max_id:
                    max_id = num
        
        next_num = max_id + 1
        node_id = f"node_{next_num}"
        position_id = f"pos_{next_num}"

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
            return {"status": "error", "message": f"Node type '{node_type_name}' not found"}

        # --- FIX: Input/Output problem (Handled by pulling from template) ---
        dynamic_inputs = [{"var": inp} for inp in template.get("dynamic", {}).get("inputs", [])]
        dynamic_outputs = template.get("dynamic", {}).get("outputs", [])

        # --- Position ---
        pos_x = payload.get("x", 100 * next_num)
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


def connection_create(payload):
    """Creates a connection between two nodes in the project graph"""
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

        # --- Extract payload ---
        source_node_id = payload.get("sourceNodeId")
        source_port = payload.get("sourcePort")
        target_node_id = payload.get("targetNodeId")
        target_port = payload.get("targetPort")

        if None in [source_node_id, source_port, target_node_id, target_port]:
            return {"status": "error", "message": "Missing connection parameters"}

        # --- Validate nodes exist ---
        nodes = graph_content.get("nodes", [])
        source_exists = any(n.get("nodeId") == source_node_id for n in nodes)
        target_exists = any(n.get("nodeId") == target_node_id for n in nodes)

        if not source_exists or not target_exists:
            return {"status": "error", "message": "Source or target node not found"}

        # --- Create connection object ---
        new_connection = {
            "sourceNodeId": source_node_id,
            "sourcePort": source_port,
            "targetNodeId": target_node_id,
            "targetPort": target_port
        }

        # --- Check for duplicate ---
        connections = graph_content.get("connections", [])
        duplicate = any(
            c.get("sourceNodeId") == source_node_id and
            c.get("sourcePort") == source_port and
            c.get("targetNodeId") == target_node_id and
            c.get("targetPort") == target_port
            for c in connections
        )

        if duplicate:
            return {"status": "error", "message": "Connection already exists"}

        # --- Add connection ---
        connections.append(new_connection)
        graph_content["connections"] = connections

        # --- Save ---
        with open(project_path, "w", encoding="utf-8") as f:
            json.dump(graph_content, f, indent=4)

        return {"status": "ok", "connection": new_connection}

    except Exception as e:
        print("ERROR in connection_create:", e)
        return {"status": "error", "message": str(e)}


def connection_delete(payload):
    """Deletes a connection between two nodes in the project graph"""
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

        # --- Extract payload ---
        source_node_id = payload.get("sourceNodeId")
        source_port = payload.get("sourcePort")
        target_node_id = payload.get("targetNodeId")
        target_port = payload.get("targetPort")

        if None in [source_node_id, source_port, target_node_id, target_port]:
            return {"status": "error", "message": "Missing connection parameters"}

        # --- Find and remove connection ---
        connections = graph_content.get("connections", [])
        original_count = len(connections)

        # Filter out the matching connection
        graph_content["connections"] = [
            c for c in connections
            if not (
                c.get("sourceNodeId") == source_node_id and
                c.get("sourcePort") == source_port and
                c.get("targetNodeId") == target_node_id and
                c.get("targetPort") == target_port
            )
        ]

        if len(graph_content["connections"]) == original_count:
            return {"status": "error", "message": "Connection not found"}

        # --- Save ---
        with open(project_path, "w", encoding="utf-8") as f:
            json.dump(graph_content, f, indent=4)

        return {
            "status": "ok",
            "deletedConnection": {
                "sourceNodeId": source_node_id,
                "sourcePort": source_port,
                "targetNodeId": target_node_id,
                "targetPort": target_port
            }
        }

    except Exception as e:
        print("ERROR in connection_delete:", e)
        return {"status": "error", "message": str(e)}

def graph_node_update_input(payload):
    """Updates a specific input value for a node"""
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

        # --- Extract payload ---
        node_id = payload.get("nodeId")
        input_index = payload.get("inputIndex")
        value = payload.get("value")

        if node_id is None or input_index is None:
            return {"status": "error", "message": "Missing nodeId or inputIndex"}

        # --- Find and update node ---
        nodes = graph_content.get("nodes", [])
        target_node = None
        
        for node in nodes:
            if node.get("nodeId") == node_id:
                target_node = node
                break

        if not target_node:
            return {"status": "error", "message": f"Node '{node_id}' not found"}

        # --- Update the input value ---
        inputs = target_node.get("input", [])
        if input_index >= len(inputs):
            return {"status": "error", "message": f"Input index {input_index} out of range"}

        inputs[input_index]["value"] = value

        # --- Save ---
        with open(project_path, "w", encoding="utf-8") as f:
            json.dump(graph_content, f, indent=4)

        return {
            "status": "ok",
            "nodeId": node_id,
            "inputIndex": input_index,
            "value": value
        }

    except Exception as e:
        print("ERROR in graph_node_update_input:", e)
        return {"status": "error", "message": str(e)}


def graph_node_move(payload):
    """Updates node position in the project graph"""
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

        # --- Extract payload ---
        node_id = payload.get("nodeId")
        position = payload.get("updates", {}).get("position", {})
        x = position.get("x")
        y = position.get("y")

        if node_id is None or x is None or y is None:
            return {"status": "error", "message": "Missing nodeId, x, or y"}

        # --- Find and update node ---
        nodes = graph_content.get("nodes", [])
        target_node = None
        
        for node in nodes:
            if node.get("nodeId") == node_id:
                target_node = node
                break

        if not target_node:
            return {"status": "error", "message": f"Node '{node_id}' not found"}

        # --- Update position ---
        target_node["position"] = {"x": x, "y": y}

        # --- Save ---
        with open(project_path, "w", encoding="utf-8") as f:
            json.dump(graph_content, f, indent=4)

        return {
            "status": "ok",
            "nodeId": node_id,
            "position": {"x": x, "y": y}
        }

    except Exception as e:
        print("ERROR in graph_node_move:", e)
        return {"status": "error", "message": str(e)}