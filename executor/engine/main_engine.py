# main_engine.py
import sys
import json
from pathlib import Path
from variable_manager import VariableManager
from node_loader import NodeLoader
from execution_manager import ExecutionManager

def main():
    if len(sys.argv) < 2:
        print("Usage: python main_engine.py <graph_file.json>")
        sys.exit(1)

    graph_path = Path(sys.argv[1]).resolve()
    if not graph_path.exists():
        print(f"[ERROR] Graph file not found: {graph_path}")
        sys.exit(1)

    with graph_path.open("r", encoding="utf-8") as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])
    connections = graph.get("connections", [])

    print(f"[ENGINE] Nodes: {len(nodes)} | Connections: {len(connections)}")

    # --- Initialize Variable Manager ---
    var_mgr = VariableManager()
    var_mgr.init_variables(nodes)
    print("[VarManager] Variables initialized:")
    print(var_mgr.variables)

    # --- Load Node Functions ---
    node_loader = NodeLoader(nodebank_path="nodebank")
    loaded_nodes = node_loader.preload_nodes(nodes)

    # --- Execution Manager ---
    exec_mgr = ExecutionManager(
        nodes=nodes,
        loaded_nodes=loaded_nodes,
        variable_manager=var_mgr,
        connections=connections
    )

    # Linear execution for now; can later switch to async/parallel
    exec_mgr.run_linear()

    print("\n[VarManager] Final variable state:")
    print(var_mgr.variables)
    print("\n[ENGINE] Done.")

if __name__ == "__main__":
    main()
