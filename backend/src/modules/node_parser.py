import ast
from pathlib import Path

class NodeParser:
    @staticmethod
    def parse_python_file(file_path: Path):
        """Extracts node metadata from Python function definitions."""
        nodes_found = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.endswith("_node"):
                    display_name = node.name.replace("_node", "").replace("_", " ").title()
                    
                    nodes_found.append({
                        "nodeId": f"{file_path.stem}_{node.name}",
                        "name": display_name,
                        "type": "script_node",
                        "scriptPath": str(file_path),
                        "entryFunction": node.name,
                        "dynamic": {
                            "inputs": [arg.arg for arg in node.args.args],
                            "outputs": ["return_value"]
                        }
                    })
        except Exception as e:
            print(f"[PARSER ERROR] {file_path.name}: {e}")
        return nodes_found