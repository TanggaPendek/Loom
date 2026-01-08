import os
import json
from pathlib import Path
import datetime
import shutil


class ProjectManager:
    def __init__(self, base_path="userdata", signal_hub=None):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.signal_hub = signal_hub

        # Optional: frontend can request current project
        if self.signal_hub:
            self.signal_hub.on("current_request", lambda _: self.signal_hub.emit("current_response", self.read_current()))

    # ===== Current project handling =====
    def _current_path(self):
        return self.base_path / "current.json"

    def init_current(self):
        """
        Initialize current.json if it doesn't exist.
        Picks the first project from folderindex.json if available.
        """
        current_file = self._current_path()
        if current_file.exists():
            return self.read_current()

        # Load folder index to pick first project
        folder_index_path = self.base_path / "folderindex.json"
        if folder_index_path.exists():
            with open(folder_index_path, "r", encoding="utf-8-sig") as f:
                index = json.load(f)
            first_project = index[0] if index else None
        else:
            first_project = None

        self.write_current(first_project)
        return first_project

    def write_current(self, project_obj):
        """
        Overwrite current.json with a single project object.
        """
        if not project_obj:
            return  # skip writing if None

        data = [project_obj]  # always store as list
        with open(self._current_path(), "w", encoding="utf-8-sig") as f:
            json.dump(data, f, indent=4)

        if self.signal_hub:
            self.signal_hub.emit("current_updated", project_obj)

    def read_current(self):
        """
        Read the current project from current.json
        """
        current_file = self._current_path()
        if not current_file.exists():
            return None
        with open(current_file, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return data[0] if data else None

    # ===== Project CRUD =====
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
        if self.signal_hub: self.signal_hub.emit("file_save", {"path": str(savefile_path)})
        with open(savefile_path, "w", encoding="utf-8-sig") as f:
            json.dump(project_data, f, indent=4)

        # Update folder index
        self.update_index()

        # Write to current.json
        self.write_current(project_data)

        if self.signal_hub:
            self.signal_hub.emit("project_init", project_data)

        return {"status": "success", "message": f"Project '{project_name}' initialized."}

    def update_project(self, project_name: str, entity_type: str = None,
                       entity_id: str = None, updates: dict = None,
                       project_updates: dict = None):
        """
        Update project changes.
        - entity_type/entity_id/updates: update or add node/connection
        - project_updates: update projectName, description, author
        """
        updates = updates or {}
        project_updates = project_updates or {}

        savefile_path = self.base_path / project_name / "savefile.json"
        if not savefile_path.exists():
            return {"status": "error", "message": f"Project '{project_name}' not found."}

        with open(savefile_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        if self.signal_hub: self.signal_hub.emit("file_loaded", {"path": str(savefile_path)})

        # Project metadata update takes priority (exclusive)
        if project_updates:
            if "projectName" in project_updates:
                data["projectName"] = project_updates["projectName"]
            data.setdefault("metadata", {})
            if "description" in project_updates:
                data["metadata"]["description"] = project_updates["description"]
            if "author" in project_updates:
                data["metadata"]["author"] = project_updates["author"]

        # Only if no project_updates, handle entity updates
        elif entity_type and entity_id:
            key = "nodes" if entity_type == "node" else "connections"
            found = False

            for item in data[key]:
                if (entity_type == "node" and item.get("nodeId") == entity_id) or \
                   (entity_type == "connection" and item.get("connectionId") == entity_id):
                    item.update(updates)
                    found = True
                    break

            if not found:
                new_item = {"nodeId": entity_id} if entity_type == "node" else {"connectionId": entity_id}
                new_item.update(updates)
                data[key].append(new_item)

        # Always update lastModified
        data.setdefault("metadata", {})
        data["metadata"]["lastModified"] = datetime.datetime.utcnow().isoformat() + "Z"

        # Save back
        if self.signal_hub: self.signal_hub.emit("file_save", {"path": str(savefile_path)})
        with open(savefile_path, "w", encoding="utf-8-sig") as f:
            json.dump(data, f, indent=4)

        # Update folder index
        self.update_index()

        # Update current.json if this is the active project
        current = self.read_current()
        if current and current.get("projectId") == data.get("projectId"):
            self.write_current(data)

        if self.signal_hub:
            self.signal_hub.emit("project_update", {
                "project_name": project_name,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "updates": updates,
                "project_updates": project_updates
            })

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

        # Clear current.json if deleted project was active
        current = self.read_current()
        if current and current.get("projectName") == project_name:
            self.write_current(None)

        if self.signal_hub:
            self.signal_hub.emit("project_delete", {"project_name": project_name})

        return {"status": "success", "message": f"Project '{project_name}' deleted."}

    def update_index(self):
        """Rebuild the folder index JSON"""
        index_path = self.base_path / "folderindex.json"
        index = []

        for folder in self.base_path.iterdir():
            if folder.is_dir():
                savefile = folder / "savefile.json"
                if savefile.exists():
                    with open(savefile, "r", encoding="utf-8-sig") as f:
                        data = json.load(f)
                        index.append({
                            "projectId": data.get("projectId"),
                            "projectName": data.get("projectName"),
                            "description": data.get("metadata", {}).get("description", ""),
                            "author": data.get("metadata", {}).get("author", ""),
                            "lastModified": data.get("metadata", {}).get("lastModified", ""),
                            "projectPath": str(savefile)
                        })

        if self.signal_hub: self.signal_hub.emit("file_save", {"path": str(index_path)})
        with open(index_path, "w", encoding="utf-8-sig") as f:
            json.dump(index, f, indent=4)

        if self.signal_hub:
            self.signal_hub.emit("project_index_update", index)

        return {"status": "success", "message": "Folder index updated."}
