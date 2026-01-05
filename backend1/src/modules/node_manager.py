import json
from pathlib import Path
import datetime

class NodeManager:
    def __init__(self, base_path="nodebank/custom"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    # ===== Helpers =====
    def generate_unique_node_id(self, base_name: str):
        """Generate unique nodeId by appending number if duplicate exists"""
        existing_ids = {f.stem for f in self.base_path.glob("*.json")}
        if base_name not in existing_ids:
            return base_name

        suffix = 1
        while f"{base_name}_{suffix}" in existing_ids:
            suffix += 1
        return f"{base_name}_{suffix}"

    def save_node_index(self, node_index_path, include_builtin=True):
        """Rebuild nodebank/nodeindex.json including custom and optionally builtin nodes"""
        index = []

        # Scan custom nodes
        for node_file in self.base_path.glob("*.json"):
            try:
                with open(node_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    index.append({
                        "nodeId": data.get("nodeId"),
                        "name": data.get("name"),
                        "type": "custom",
                        "metadata": data.get("metadata", {})
                    })
            except Exception as e:
                print(f"Error reading {node_file}: {e}")

        # Optionally scan builtin nodes
        if include_builtin:
            builtin_path = self.base_path.parent / "builtin"
            if builtin_path.exists():
                for node_file in builtin_path.glob("*.json"):
                    try:
                        with open(node_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            index.append({
                                "nodeId": data.get("nodeId"),
                                "name": data.get("name"),
                                "type": "builtin",
                                "metadata": data.get("metadata", {})
                            })
                    except Exception as e:
                        print(f"Error reading builtin node {node_file}: {e}")

        # Save the merged index
        with open(node_index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=4)
        print(f"Node index updated ({len(index)} nodes).")


    # ===== Node Operations =====
    def add_node(self, node_data, node_index_path):
        """Add a new node (raw python + metadata) with unique ID"""
        base_id = node_data.get("nodeId")
        func_code = node_data.pop("function_code", None)
        if not base_id or not func_code:
            raise ValueError("Payload must include 'nodeId' and 'function_code'")

        node_id = self.generate_unique_node_id(base_id)

        # Save raw Python file
        py_file_path = self.base_path / f"{node_id}.py"
        with open(py_file_path, "w", encoding="utf-8") as f:
            f.write(func_code)

        # Save metadata JSON
        node_data["nodeId"] = node_id
        node_data["file"] = f"{node_id}.py"
        json_file_path = self.base_path / f"{node_id}.json"
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(node_data, f, indent=4)

        self.save_node_index(node_index_path)
        print(f"Node '{node_id}' added and indexed.")
        return node_id

    def update_node(self, node_data, node_index_path):
        """Update existing node metadata"""
        node_id = node_data.get("nodeId")
        if not node_id:
            raise ValueError("Payload must include 'nodeId'")

        node_file = self.base_path / f"{node_id}.json"
        if not node_file.exists():
            raise FileNotFoundError(f"Node '{node_id}' does not exist.")

        with open(node_file, "r", encoding="utf-8") as f:
            existing = json.load(f)

        existing.update(node_data)
        existing.setdefault("metadata", {})
        existing["metadata"]["lastModified"] = datetime.datetime.utcnow().isoformat() + "Z"

        with open(node_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4)

        self.save_node_index(node_index_path)
        print(f"Node '{node_id}' updated.")

    def delete_node(self, node_id, node_index_path):
        """Delete a node (both .json and .py)"""
        node_file = self.base_path / f"{node_id}.json"
        py_file = self.base_path / f"{node_id}.py"

        if not node_file.exists():
            raise FileNotFoundError(f"Node '{node_id}' does not exist.")

        node_file.unlink()
        if py_file.exists():
            py_file.unlink()

        self.save_node_index(node_index_path)
        print(f"Node '{node_id}' deleted.")

    def print_node_index(self, node_index_path):
        """Print node index"""
        if node_index_path.exists():
            with open(node_index_path, "r", encoding="utf-8") as f:
                index = json.load(f)
            print(json.dumps(index, indent=4))
        else:
            print("No node index found. Run addnode first.")




#Automated Test Pending