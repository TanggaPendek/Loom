import os
import json
from pathlib import Path
import datetime
import shutil
from .storage_manager import StorageManager

class ProjectManager:
    def __init__(self, base_path="userdata", signal_hub=None):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.signal_hub = signal_hub
        StorageManager.init_storage()

        if self.signal_hub:
            self.signal_hub.on("current_request", lambda _: self.signal_hub.emit("current_response", self.read_current()))

    # ===== Current project handling =====
    def write_current(self, project_obj):
        """Save active project to state.json"""
        if not project_obj:
            return

        state = StorageManager.get_state()
        state["active_project"] = project_obj
        StorageManager.save_state(state)

        if self.signal_hub:
            self.signal_hub.emit("current_updated", project_obj)

    def read_current(self):
        """Read active project from state.json"""
        state = StorageManager.get_state()
        return state.get("active_project")

    def init_current(self):
        current_data = self.read_current()
        if current_data:
            return current_data

        folder_index_path = self.base_path / "folderindex.json"
        if folder_index_path.exists():
            with open(folder_index_path, "r", encoding="utf-8-sig") as f:
                index = json.load(f)
            first_project = index[0] if index else None
        else:
            first_project = None

        self.write_current(first_project)
        return first_project

    # ===== Project CRUD =====
    def init_project(self, project_name=None, description=None, author="author"):
        folder_count = len([d for d in self.base_path.iterdir() if d.is_dir()]) + 1

        project_name = project_name or f"Project_{folder_count}"
        base_name = project_name
        suffix = 1
        project_path = self.base_path / project_name

        while project_path.exists():
            project_name = f"{base_name}_{suffix}"
            project_path = self.base_path / project_name
            suffix += 1

        description = description or f"description for {project_name}"
        savefile_path = project_path / "savefile.json"
        project_path.mkdir(parents=True, exist_ok=True)

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

        if self.signal_hub: self.signal_hub.emit("file_save", {"path": str(savefile_path)})
        with open(savefile_path, "w", encoding="utf-8-sig") as f:
            json.dump(project_data, f, indent=4)

        self.update_index()
        self.write_current(project_data)

        if self.signal_hub:
            self.signal_hub.emit("project_init", project_data)

        return {"status": "success", "message": f"Project '{project_name}' initialized."}

    def update_project(self, project_name: str, entity_type: str = None,
                       entity_id: str = None, updates: dict = None,
                       project_updates: dict = None):
        savefile_path = self.base_path / project_name / "savefile.json"
        if not savefile_path.exists():
            return {"status": "error", "message": f"Project '{project_name}' not found."}

        with open(savefile_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        if project_updates:
            if "projectName" in project_updates:
                data["projectName"] = project_updates["projectName"]
            data.setdefault("metadata", {})
            if "description" in project_updates:
                data["metadata"]["description"] = project_updates["description"]
            if "author" in project_updates:
                data["metadata"]["author"] = project_updates["author"]

        elif entity_type and entity_id:
            key = "nodes" if entity_type == "node" else "connections"
            found = False
            for item in data[key]:
                if (entity_type == "node" and item.get("nodeId") == entity_id) or \
                   (entity_type == "connection" and item.get("connectionId") == entity_id):
                    item.update(updates or {})
                    found = True
                    break
            if not found:
                new_item = {"nodeId": entity_id} if entity_type == "node" else {"connectionId": entity_id}
                new_item.update(updates or {})
                data[key].append(new_item)

        data.setdefault("metadata", {})
        data["metadata"]["lastModified"] = datetime.datetime.utcnow().isoformat() + "Z"

        with open(savefile_path, "w", encoding="utf-8-sig") as f:
            json.dump(data, f, indent=4)

        self.update_index()

        current = self.read_current()
        if current and current.get("projectId") == data.get("projectId"):
            self.write_current(data)

        return {"status": "success", "message": f"Project '{project_name}' updated."}

    def delete_project(self, project_name: str):
        project_path = self.base_path / project_name
        if not project_path.exists():
            return {"status": "error", "message": f"Project '{project_name}' not found."}

        shutil.rmtree(project_path)
        self.update_index()

        current = self.read_current()
        if current and current.get("projectName") == project_name:
            state = StorageManager.get_state()
            state["active_project"] = None
            StorageManager.save_state(state)

        return {"status": "success", "message": f"Project '{project_name}' deleted."}

    def change_project(self, project_id: str):
        folder_index_path = self.base_path / "folderindex.json"
        if not folder_index_path.exists():
            return None
        
        with open(folder_index_path, "r", encoding="utf-8-sig") as f:
            index = json.load(f)
            
        project_obj = next((p for p in index if p["projectId"] == project_id), None)
        if project_obj:
            self.write_current(project_obj)
            return project_obj
        return None

    def update_index(self):
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

        with open(index_path, "w", encoding="utf-8-sig") as f:
            json.dump(index, f, indent=4)
        return {"status": "success", "message": "Index updated."}