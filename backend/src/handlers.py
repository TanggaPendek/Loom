"""
Loom Backend Request Handlers

This module contains all signal handlers for backend operations including:
- Engine control and execution
- Project management
- Graph manipulation (nodes and connections)
- File I/O utilities
"""

import sys
import json
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from .config import ROOT_DIR, USERDATA_PATH, NODE_INDEX_PATH


# ============================================================================
# Path Constants
# ============================================================================

PROJECT_INDEX_PATH = USERDATA_PATH / "projectindex.json"
STATE_PATH = USERDATA_PATH / "state.json"
NODE_INDEX_PATH = ROOT_DIR / "nodebank" / "nodeindex.json"


# ============================================================================
# Helper Functions - File I/O
# ============================================================================

def load_json_file(file_path: Path, default=None) -> Optional[Dict]:
    """Safely load JSON file with error handling."""
    if not file_path.exists():
        return default
    
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return default


def save_json_file(file_path: Path, data: Dict) -> bool:
    """Safely save JSON file with error handling."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False


def get_project_path_from_state() -> Optional[Path]:
    """Load project path from state.json."""
    state_data = load_json_file(STATE_PATH)
    if not state_data:
        return None
    
    project_path_str = state_data.get("projectPath")
    if not project_path_str:
        return None
    
    return Path(project_path_str)


def load_graph_from_state() -> Optional[Dict]:
    """Load graph content from current project in state.json."""
    project_path = get_project_path_from_state()
    if not project_path or not project_path.exists():
        return None
    
    return load_json_file(project_path)


# ============================================================================
# Helper Functions - Node ID Management
# ============================================================================

def get_next_node_id(nodes: list) -> tuple[str, str]:
    """
    Generate next sequential node ID and position ID.
    
    Args:
        nodes: List of existing nodes
        
    Returns:
        Tuple of (node_id, position_id) e.g. ("node_5", "pos_5")
    """
    max_id = 0
    for node in nodes:
        match = re.search(r'node_(\d+)', node.get("nodeId", "0"))
        if match:
            num = int(match.group(1))
            if num > max_id:
                max_id = num
    
    next_num = max_id + 1
    return f"node_{next_num}", f"pos_{next_num}"


# ============================================================================
# Engine Control Handlers
# ============================================================================

def launch_engine(payload: Dict) -> None:
    """Launch the executor engine as a subprocess."""
    print("[BACKEND] Launching executor engine via signal...")
    engine_path = ROOT_DIR / "executor" / "engine" / "main_engine.py"
    
    try:
        subprocess.Popen([sys.executable, str(engine_path)])
    except Exception as e:
        print(f"[BACKEND ERROR] Failed to launch engine: {e}")


def handle_engine_output(payload: Dict) -> None:
    """Process engine output and forward to appropriate channels."""
    line = payload.get("line", "")
    if line.startswith("PROGRESS:"):
        print(f"UI Update: {line}")
    else:
        print(f"Engine Log: {line}")


def on_finished(payload: Dict) -> None:
    """Handle engine execution completion."""
    exit_code = payload.get("exit_code")
    print(f"System: Execution stopped with code {exit_code}")


# ============================================================================
# System Handlers
# ============================================================================

def log_signal(payload: Dict) -> None:
    """Log signal events when DEBUG mode is enabled."""
    if os.getenv("DEBUG", "False").lower() == "true":
        print(f"[SIGNAL] {payload}")


def get_startup_payload() -> Dict:
    """
    Gather all startup data needed by the frontend.
    
    Returns:
        Dictionary containing setting, current, project_index, and node_index data
    """
    files = {
        "setting": USERDATA_PATH / "setting.json",
        "current": USERDATA_PATH / "current.json",
        "project_index": PROJECT_INDEX_PATH,
        "node_index": NODE_INDEX_PATH
    }
    
    result = {}
    for key, path in files.items():
        result[key] = load_json_file(path)
    
    return result


# ============================================================================
# Project Handlers
# ============================================================================

def handle_load_graph(payload: Optional[Dict] = None) -> Dict:
    """
    Load graph data for the currently active project.
    
    Returns:
        Dictionary containing metadata and graph content, or error
    """
    if not STATE_PATH.exists():
        return {"status": "error", "message": "state.json missing"}
    
    try:
        state_data = load_json_file(STATE_PATH)
        if not state_data:
            return {"status": "error", "message": "Failed to load state.json"}
        
        project_path = get_project_path_from_state()
        if not project_path:
            return {"status": "error", "message": "No projectPath in state"}
        
        if not project_path.exists():
            return {"status": "error", "message": "Graph file not found"}
        
        graph_content = load_json_file(project_path)
        if not graph_content:
            return {"status": "error", "message": "Failed to load graph file"}
        
        return {
            "metadata": state_data,
            "graph": graph_content
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


def project_load_request(payload: Dict) -> Dict:
    """
    Load a project by ID and update state.json.
    
    Args:
        payload: Must contain 'projectId'
        
    Returns:
        Status dictionary
    """
    try:
        project_id = payload.get("projectId")
        if not project_id:
            return {"status": "error", "message": "No projectId provided"}
        
        project_index = load_json_file(PROJECT_INDEX_PATH)
        if not project_index:
            return {"status": "error", "message": "Project index not found"}
        
        # Find the project
        project = next(
            (p for p in project_index if p.get("projectId") == project_id),
            None
        )
        
        if not project:
            return {"status": "error", "message": f"Project '{project_id}' not found"}
        
        # Update state
        if not save_json_file(STATE_PATH, project):
            return {"status": "error", "message": "Failed to update state"}
        
        return {"status": "ok", "projectId": project_id}
        
    except Exception as e:
        print(f"ERROR in project_load_request: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# Graph Node Handlers
# ============================================================================

def graph_node_add(payload: Dict) -> Dict:
    """
    Add a new node to the project graph.
    
    Args:
        payload: Must contain 'type' (node type name), optional 'x', 'y' for position
        
    Returns:
        Status dictionary with created node data
    """
    try:
        # Load current graph
        graph_content = load_graph_from_state()
        if not graph_content:
            return {"status": "error", "message": "Failed to load project graph"}
        
        project_path = get_project_path_from_state()
        if not project_path:
            return {"status": "error", "message": "No active project"}
        
        nodes = graph_content.get("nodes", [])
        
        # Generate unique node ID
        node_id, position_id = get_next_node_id(nodes)
        
        # Load node template
        node_index = load_json_file(NODE_INDEX_PATH)
        if not node_index:
            return {"status": "error", "message": "Node index not found"}
        
        node_type_name = payload.get("type")
        if not node_type_name:
            return {"status": "error", "message": "No node type provided"}
        
        # Find template
        template = next(
            (n for n in node_index if n["name"].lower() == node_type_name.lower()),
            None
        )
        
        if not template:
            return {"status": "error", "message": f"Node type '{node_type_name}' not found"}
        
        # Build node from template
        dynamic_inputs = [{"var": inp} for inp in template.get("dynamic", {}).get("inputs", [])]
        dynamic_outputs = template.get("dynamic", {}).get("outputs", [])
        
        pos_x = payload.get("x", 100 * int(node_id.split("_")[1]))
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
        
        # Add to graph and save
        nodes.append(new_node)
        graph_content["nodes"] = nodes
        
        if not save_json_file(project_path, graph_content):
            return {"status": "error", "message": "Failed to save graph"}
        
        return {"status": "ok", "node": new_node}
        
    except Exception as e:
        print(f"ERROR in graph_node_add: {e}")
        return {"status": "error", "message": str(e)}


def graph_node_delete(payload: Dict) -> Dict:
    """
    Delete a node and its connections from the project graph.
    
    Args:
        payload: Must contain 'nodeId'
        
    Returns:
        Status dictionary
    """
    try:
        graph_content = load_graph_from_state()
        if not graph_content:
            return {"status": "error", "message": "Failed to load project graph"}
        
        project_path = get_project_path_from_state()
        if not project_path:
            return {"status": "error", "message": "No active project"}
        
        target_id = payload.get("nodeId")
        if not target_id:
            return {"status": "error", "message": "No nodeId provided"}
        
        # Remove the node
        original_count = len(graph_content.get("nodes", []))
        graph_content["nodes"] = [
            n for n in graph_content.get("nodes", [])
            if n.get("nodeId") != target_id
        ]
        
        if len(graph_content["nodes"]) == original_count:
            return {"status": "error", "message": f"Node '{target_id}' not found"}
        
        # Remove associated connections
        if "connections" in graph_content:
            graph_content["connections"] = [
                c for c in graph_content.get("connections", [])
                if c.get("sourceNodeId") != target_id and c.get("targetNodeId") != target_id
            ]
        
        # Save
        if not save_json_file(project_path, graph_content):
            return {"status": "error", "message": "Failed to save graph"}
        
        return {"status": "ok", "deletedNodeId": target_id}
        
    except Exception as e:
        print(f"ERROR in graph_node_delete: {e}")
        return {"status": "error", "message": str(e)}


def graph_node_update_input(payload: Dict) -> Dict:
    """
    Update a specific input value for a node.
    
    Note: If the input has an active connection, the value is preserved
    but will be ignored during execution (connection takes priority).
    
    Args:
        payload: Must contain 'nodeId', 'inputIndex', 'value'
        
    Returns:
        Status dictionary
    """
    try:
        graph_content = load_graph_from_state()
        if not graph_content:
            return {"status": "error", "message": "Failed to load project graph"}
        
        project_path = get_project_path_from_state()
        if not project_path:
            return {"status": "error", "message": "No active project"}
        
        node_id = payload.get("nodeId")
        input_index = payload.get("inputIndex")
        value = payload.get("value")
        
        if node_id is None or input_index is None:
            return {"status": "error", "message": "Missing nodeId or inputIndex"}
        
        # Find the node
        nodes = graph_content.get("nodes", [])
        target_node = next(
            (n for n in nodes if n.get("nodeId") == node_id),
            None
        )
        
        if not target_node:
            return {"status": "error", "message": f"Node '{node_id}' not found"}
        
        # Update the input value
        inputs = target_node.get("input", [])
        if input_index >= len(inputs):
            return {"status": "error", "message": f"Input index {input_index} out of range"}
        
        # Preserve value even if connection exists
        inputs[input_index]["value"] = value
        
        # Save
        if not save_json_file(project_path, graph_content):
            return {"status": "error", "message": "Failed to save graph"}
        
        return {
            "status": "ok",
            "nodeId": node_id,
            "inputIndex": input_index,
            "value": value
        }
        
    except Exception as e:
        print(f"ERROR in graph_node_update_input: {e}")
        return {"status": "error", "message": str(e)}


def graph_node_move(payload: Dict) -> Dict:
    """
    Update node position in the project graph.
    
    Args:
        payload: Must contain 'nodeId' and 'updates' with 'position' {x, y}
        
    Returns:
        Status dictionary
    """
    try:
        graph_content = load_graph_from_state()
        if not graph_content:
            return {"status": "error", "message": "Failed to load project graph"}
        
        project_path = get_project_path_from_state()
        if not project_path:
            return {"status": "error", "message": "No active project"}
        
        node_id = payload.get("nodeId")
        position = payload.get("updates", {}).get("position", {})
        x = position.get("x")
        y = position.get("y")
        
        if node_id is None or x is None or y is None:
            return {"status": "error", "message": "Missing nodeId, x, or y"}
        
        # Find and update node
        nodes = graph_content.get("nodes", [])
        target_node = next(
            (n for n in nodes if n.get("nodeId") == node_id),
            None
        )
        
        if not target_node:
            return {"status": "error", "message": f"Node '{node_id}' not found"}
        
        target_node["position"] = {"x": x, "y": y}
        
        # Save
        if not save_json_file(project_path, graph_content):
            return {"status": "error", "message": "Failed to save graph"}
        
        return {
            "status": "ok",
            "nodeId": node_id,
            "position": {"x": x, "y": y}
        }
        
    except Exception as e:
        print(f"ERROR in graph_node_move: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# Connection Handlers
# ============================================================================

def connection_create(payload: Dict) -> Dict:
    """
    Create a connection between two nodes.
    
    Args:
        payload: Must contain sourceNodeId, sourcePort, targetNodeId, targetPort
        
    Returns:
        Status dictionary with connection data
    """
    try:
        graph_content = load_graph_from_state()
        if not graph_content:
            return {"status": "error", "message": "Failed to load project graph"}
        
        project_path = get_project_path_from_state()
        if not project_path:
            return {"status": "error", "message": "No active project"}
        
        # Extract parameters
        source_node_id = payload.get("sourceNodeId")
        source_port = payload.get("sourcePort")
        target_node_id = payload.get("targetNodeId")
        target_port = payload.get("targetPort")
        
        if None in [source_node_id, source_port, target_node_id, target_port]:
            return {"status": "error", "message": "Missing connection parameters"}
        
        # Validate nodes exist
        nodes = graph_content.get("nodes", [])
        source_exists = any(n.get("nodeId") == source_node_id for n in nodes)
        target_exists = any(n.get("nodeId") == target_node_id for n in nodes)
        
        if not source_exists or not target_exists:
            return {"status": "error", "message": "Source or target node not found"}
        
        # Create connection
        new_connection = {
            "sourceNodeId": source_node_id,
            "sourcePort": source_port,
            "targetNodeId": target_node_id,
            "targetPort": target_port
        }
        
        # Check for duplicate
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
        
        # Add and save
        connections.append(new_connection)
        graph_content["connections"] = connections
        
        if not save_json_file(project_path, graph_content):
            return {"status": "error", "message": "Failed to save graph"}
        
        return {"status": "ok", "connection": new_connection}
        
    except Exception as e:
        print(f"ERROR in connection_create: {e}")
        return {"status": "error", "message": str(e)}


def connection_delete(payload: Dict) -> Dict:
    """
    Delete a connection between two nodes.
    
    Args:
        payload: Must contain sourceNodeId, sourcePort, targetNodeId, targetPort
        
    Returns:
        Status dictionary
    """
    try:
        graph_content = load_graph_from_state()
        if not graph_content:
            return {"status": "error", "message": "Failed to load project graph"}
        
        project_path = get_project_path_from_state()
        if not project_path:
            return {"status": "error", "message": "No active project"}
        
        # Extract parameters
        source_node_id = payload.get("sourceNodeId")
        source_port = payload.get("sourcePort")
        target_node_id = payload.get("targetNodeId")
        target_port = payload.get("targetPort")
        
        if None in [source_node_id, source_port, target_node_id, target_port]:
            return {"status": "error", "message": "Missing connection parameters"}
        
        # Remove connection
        connections = graph_content.get("connections", [])
        original_count = len(connections)
        
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
        
        # Save
        if not save_json_file(project_path, graph_content):
            return {"status": "error", "message": "Failed to save graph"}
        
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
        print(f"ERROR in connection_delete: {e}")
        return {"status": "error", "message": str(e)}