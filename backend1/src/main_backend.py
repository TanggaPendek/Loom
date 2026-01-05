import sys
import json
from pathlib import Path
from .modules.project_manager import ProjectManager
from .modules.node_manager import NodeManager

# ===== Paths =====
ROOT_DIR = Path(__file__).parent.parent.parent
NODEBANK_PATH = ROOT_DIR / "nodebank"
CUSTOM_NODE_PATH = NODEBANK_PATH / "custom"
BUILTIN_NODE_PATH = NODEBANK_PATH / "builtin"
NODE_INDEX_PATH = NODEBANK_PATH / "nodeindex.json"

# Ensure folders exist
CUSTOM_NODE_PATH.mkdir(parents=True, exist_ok=True)
BUILTIN_NODE_PATH.mkdir(parents=True, exist_ok=True)

# ===== Managers =====
project_backend = ProjectManager()
node_backend = NodeManager(base_path=CUSTOM_NODE_PATH)

# ===== Helper =====
def load_payload(payload_arg):
    """Load payload from file or JSON string"""
    path = Path(payload_arg)
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return json.loads(payload_arg)

# ===== Main =====
def main():
    if len(sys.argv) < 2:
        print("Usage: python -m backend1.src.main_backend <command> [args]")
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        # ===== Project commands =====
        if command == "init":
            project_name = sys.argv[2] if len(sys.argv) > 2 else None
            description = sys.argv[3] if len(sys.argv) > 3 else None
            result = project_backend.init_project(project_name, description)
            print(result)

        elif command == "save":
            project_name = sys.argv[2] if len(sys.argv) > 2 else None
            payload = load_payload(sys.argv[3])
            entity_type = payload.get("entity_type")
            entity_id = payload.get("entity_id")
            updates = payload.get("updates")
            project_updates = payload.get("project_updates")
            result = project_backend.update_project(
                project_name, entity_type=entity_type, entity_id=entity_id,
                updates=updates, project_updates=project_updates
            )
            print(result)

        elif command == "index":
            result = project_backend.update_index()
            print(result)

        elif command == "delete":
            project_name = sys.argv[2] if len(sys.argv) > 2 else None
            result = project_backend.delete_project(project_name)
            print(result)

        # ===== Node commands =====
        elif command == "addnode":
            payload = load_payload(sys.argv[2])
            node_backend.add_node(payload, NODE_INDEX_PATH)

        elif command == "updatenode":
            payload = load_payload(sys.argv[2])
            node_backend.update_node(payload, NODE_INDEX_PATH)

        elif command == "deletenode":
            node_backend.delete_node(sys.argv[2], NODE_INDEX_PATH)

        elif command == "nodeindex":
            node_backend.print_node_index(NODE_INDEX_PATH)

        else:
            print(f"Unknown command '{command}'")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()




#Update to signal pending