# node_loader.py
import importlib.util
from pathlib import Path

class NodeLoader:
    def __init__(self, nodebank_path="nodebank"):
        self.nodebank_path = Path(nodebank_path)
        self.loaded_nodes = {}  # nodeId -> function


    def load_node_function(self, node: dict):
        """
        Load a node script from nodebank dynamically.
        Node is a dictionary from the JSON.
        Uses 'ref' as folder (builtin/custom) and 'name' as script/function name.
        """
        node_type = node.get("ref", "builtin")  # folder: builtin or custom
        node_name = node.get("name")            # script & function name

        script_path = self.nodebank_path / node_type / f"{node_name}.py"
        if not script_path.exists():
            raise FileNotFoundError(f"\nNode script not found: {script_path}")

        spec = importlib.util.spec_from_file_location(node_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        func = getattr(module, node_name, None)
        if func is None:
            raise AttributeError(f"\nFunction '{node_name}' not found in {script_path}")

        return func

    def preload_nodes(self, nodes: list):
        """
        Preload all nodes from project JSON.
        nodes: list of node dicts
        """
        for node in nodes:
            node_id = node.get("nodeId")
            try:
                func = self.load_node_function(node)  # pass the dict, not a string
                self.loaded_nodes[node_id] = func
            except Exception as e:
                print(f"\n[WARNING] Failed to load node {node_id} ({node.get('ref', 'builtin')}): {e}")

        print(f"\n[NodeLoader] Preloaded {len(self.loaded_nodes)} nodes.")
        return self.loaded_nodes




#Automated Test Pending