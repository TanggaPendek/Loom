import ast
from pathlib import Path

class NodeParser:
    @staticmethod
    def parse_python_file(file_path: Path):
        nodes_found = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            file_stem = file_path.stem

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.endswith("_node"):
                    display_name = node.name.replace("_node", "").replace("_", " ").title()
                    unique_id = node.name if node.name == file_stem else f"{file_stem}_{node.name}"

                    inputs = [arg.arg for arg in node.args.args]

                    outputs = []
                    for sub_node in ast.walk(node):
                        if isinstance(sub_node, ast.Return) and sub_node.value is not None:
                            value = sub_node.value

                            # Tuple return
                            if isinstance(value, ast.Tuple):
                                for elt in value.elts:
                                    # Try to extract variable/attribute name
                                    if isinstance(elt, ast.Name):
                                        outputs.append(elt.id)
                                    elif isinstance(elt, ast.Attribute):
                                        outputs.append(elt.attr)
                                    elif isinstance(elt, ast.Constant):
                                        outputs.append(str(elt.value))
                                    else:
                                        outputs.append("return")
                            else:
                                # Single return
                                if isinstance(value, ast.Name):
                                    outputs.append(value.id)
                                elif isinstance(value, ast.Attribute):
                                    outputs.append(value.attr)
                                elif isinstance(value, ast.Constant):
                                    outputs.append(str(value.value))
                                else:
                                    outputs.append("return")
                    
                    nodes_found.append({
                        "nodeId": unique_id,
                        "name": display_name,
                        "type": "script_node",
                        "scriptPath": str(file_path),
                        "entryFunction": node.name,
                        "dynamic": {
                            "inputs": inputs,
                            "outputs": outputs
                        }
                    })

        except Exception as e:
            print(f"[PARSER ERROR] {file_path.name}: {e}")
        return nodes_found
