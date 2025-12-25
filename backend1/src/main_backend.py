import sys
from .modules.project_manager import ProjectManager
import json
import os

def main():
    backend = ProjectManager()

    if len(sys.argv) < 2:
        print("Usage: python main_backend.py <command> [project_name] [description_or_json]")
        sys.exit(1)

    command = sys.argv[1].lower()
    project_name = sys.argv[2] if len(sys.argv) > 2 else None

    if command == "init":
        description = sys.argv[3] if len(sys.argv) > 3 else None
        result = backend.init_project(project_name, description)
        print(result)

    elif command == "save":
        if len(sys.argv) < 4:
            print("Usage: save <project_name> <json_updates_or_project_updates>")
            sys.exit(1)

    

        payload_arg = sys.argv[3]

        # Detect if argument is a file
        if os.path.isfile(payload_arg):
            try:
                with open(payload_arg, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            except json.JSONDecodeError as e:
                print("Invalid JSON in file:", e)
                sys.exit(1)
        else:
            try:
                payload = json.loads(payload_arg)
            except json.JSONDecodeError as e:
                print("Invalid JSON:", e)
                sys.exit(1)


        entity_type = payload.get("entity_type")
        entity_id = payload.get("entity_id")
        updates = payload.get("updates")
        project_updates = payload.get("project_updates")

        result = backend.update_project(   # call new ProjectManager method
            project_name,
            entity_type=entity_type,
            entity_id=entity_id,
            updates=updates,
            project_updates=project_updates
        )
        print(result)



    elif command == "index":
        result = backend.update_index()
        print(result)

    elif command == "delete":
        if not project_name:
            print("Usage: delete <project_name>")
            sys.exit(1)
        result = backend.delete_project(project_name)
        print(result)

    else:
        print(f"Unknown command '{command}'. Available: init, save, index")


if __name__ == "__main__":
    main()
