import os
import json
from pathlib import Path
import datetime
import shutil


class ProjectManager:
    def __init__(self, base_path="userdata"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def init_project(self, project_name=None, description=None, author="author"):
        """
        Create folder structure and initial JSON for a new project.
        Auto-increments project name if folder already exists.
        """
        folder_count = len([d for d in self.base_path.iterdir() if d.is_dir()]) + 1

        # Default project name
        project_name = project_name or f"Project_{folder_count}"
        base_name = project_name
        suffix = 1
        project_path = self.base_path / project_name

        # Auto-increment if folder already exists
        while project_path.exists():
            project_name = f"{base_name}_{suffix}"
            project_path = self.base_path / project_name
            suffix += 1

        description = description or f"description for {project_name}"
        savefile_path = project_path / "savefile.json"
        project_path.mkdir(parents=True, exist_ok=True)

        # Default project structure
        project_data = {
            "projectId": f"proj_{folder_count:03d}",
            "projectName": project_name,
            "projectPath": str(savefile_path),
            "metadata": {
                "author": author,
                "description": description,
                "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
                "lastModified": datetime.datetime.utcnow().isoformat() + "Z"
            },
            "nodes": [],
            "connections": []
        }

        # Save initial JSON
        with open(savefile_path, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4)

        # Update folder index
        self.update_index()

        return {"status": "success", "message": f"Project '{project_name}' initialized."}


    def save_project(self, project_name: str, entity_type: str = None,
                    entity_id: str = None, updates: dict = None,
                    project_updates: dict = None):
        """
        Save project changes.
        - entity_type/entity_id/updates: update or add node/connection
        - project_updates: update projectName, description, author
        """
        updates = updates or {}
        project_updates = project_updates or {}

        savefile_path = self.base_path / project_name / "savefile.json"
        if not savefile_path.exists():
            return {"status": "error", "message": f"Project '{project_name}' not found."}

        with open(savefile_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Update or add node/connection
        if entity_type and entity_id:
            key = "nodes" if entity_type == "node" else "connections"
            found = False

            for item in data[key]:
                if (entity_type == "node" and item.get("nodeId") == entity_id) or \
                (entity_type == "connection" and item.get("connectionId") == entity_id):
                    item.update(updates)
                    found = True
                    break

            if not found:
                # Add new node/connection
                new_item = {"nodeId": entity_id} if entity_type == "node" else {"connectionId": entity_id}
                new_item.update(updates)
                data[key].append(new_item)

        # Update project-level metadata
        if project_updates:
            if "projectName" in project_updates:
                data["projectName"] = project_updates["projectName"]
            data.setdefault("metadata", {})
            if "description" in project_updates:
                data["metadata"]["description"] = project_updates["description"]
            if "author" in project_updates:
                data["metadata"]["author"] = project_updates["author"]

        # Always update lastModified
        data.setdefault("metadata", {})
        data["metadata"]["lastModified"] = datetime.datetime.utcnow().isoformat() + "Z"

        # Save back
        with open(savefile_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        # Update folder index
        self.update_index()

        return {"status": "success", "message": f"Project '{project_name}' updated."}



    def delete_project(self, project_name: str):
        """
        Delete a project folder and update folder index.
        """
        project_path = self.base_path / project_name
        if not project_path.exists():
            return {"status": "error", "message": f"Project '{project_name}' not found."}

        # Delete the project folder
        shutil.rmtree(project_path)

        # Update folder index
        self.update_index()

        return {"status": "success", "message": f"Project '{project_name}' deleted."}


    def update_index(self):
            """Rebuild the folder index JSON"""
            index_path = self.base_path / "folderindex.json"
            index = []

            for folder in self.base_path.iterdir():
                if folder.is_dir():
                    savefile = folder / "savefile.json"
                    if savefile.exists():
                        with open(savefile, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            index.append({
                                "projectId": data.get("projectId"),
                                "projectName": data.get("projectName"),
                                "description": data.get("metadata", {}).get("description", ""),
                                "author": data.get("metadata", {}).get("author", ""),
                                "lastModified": data.get("metadata", {}).get("lastModified", ""),
                                "projectPath": str(savefile)
                            })

            with open(index_path, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=4)

            return {"status": "success", "message": "Folder index updated."}