# modules/project_manager.py
import json, datetime, shutil
from pathlib import Path
from .validator import Validator

class ProjectManager:
    def __init__(self, base_path="userdata", signal_hub=None):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.signal_hub = signal_hub
        self.validator = Validator(signal_hub=signal_hub)

        # ===== Subscribe =====
        if signal_hub:
            signal_hub.on("project_init_request", self._handle_init)
            signal_hub.on("project_update_request", self._handle_update)
            signal_hub.on("project_delete_request", self._handle_delete)
            signal_hub.on("project_index_request", lambda _: self.update_index())

    # ===== Handlers =====
    def _handle_init(self, payload):
        try:
            self.validator.validate_project_payload(payload or {})
            self.init_project(**(payload or {}))
        except Exception as e:
            if self.signal_hub: self.signal_hub.emit("validation_error", {"message": str(e)})

    def _handle_update(self, payload):
        try:
            self.validator.validate_project_payload(payload or {})
            self.update_project(**(payload or {}))
        except Exception as e:
            if self.signal_hub: self.signal_hub.emit("validation_error", {"message": str(e)})

    def _handle_delete(self, payload):
        try:
            if not payload or "projectName" not in payload:
                raise ValueError("Missing projectName")
            self.delete_project(payload["projectName"])
        except Exception as e:
            if self.signal_hub: self.signal_hub.emit("validation_error", {"message": str(e)})

    # ===== Main Functions (same as before, emit signals) =====
    def init_project(self, project_name=None, description=None, author="author"):
        folder_count = len([d for d in self.base_path.iterdir() if d.is_dir()]) + 1
        project_name = project_name or f"Project_{folder_count}"
        project_path = self.base_path / project_name
        suffix = 1
        base_name = project_name
        while project_path.exists():
            project_name = f"{base_name}_{suffix}"
            project_path = self.base_path / project_name
            suffix += 1

        description = description or f"description for {project_name}"
        project_data = {
            "projectId": f"proj_{folder_count:03d}",
            "projectName": project_name,
            "projectPath": str(project_path / "savefile.json"),
            "metadata": {"author": author, "description": description,
                         "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
                         "lastModified": datetime.datetime.utcnow().isoformat() + "Z"},
            "nodes": [], "connections": []
        }
        project_path.mkdir(parents=True, exist_ok=True)
        savefile_path = project_path / "savefile.json"
        with open(savefile_path, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4)
        if self.signal_hub: self.signal_hub.emit("file_save", {"path": str(savefile_path)})
        self.update_index()
        if self.signal_hub: self.signal_hub.emit("project_init", project_data)
        return project_data

    def update_project(self, project_name, entity_type=None, entity_id=None, updates=None, project_updates=None):
        # similar to your previous code, plus validation
        updates = updates or {}
        project_updates = project_updates or {}
        savefile_path = self.base_path / project_name / "savefile.json"
        if not savefile_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found.")
        with open(savefile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if self.signal_hub: self.signal_hub.emit("file_loaded", {"path": str(savefile_path)})

        if project_updates:
            data["projectName"] = project_updates.get("projectName", data["projectName"])
            data.setdefault("metadata", {})
            data["metadata"]["description"] = project_updates.get("description", data["metadata"].get("description"))
            data["metadata"]["author"] = project_updates.get("author", data["metadata"].get("author"))
        elif entity_type and entity_id:
            key = "nodes" if entity_type == "node" else "connections"
            found = False
            for item in data[key]:
                if (entity_type=="node" and item.get("nodeId")==entity_id) or (entity_type=="connection" and item.get("connectionId")==entity_id):
                    item.update(updates)
                    found=True
                    break
            if not found:
                new_item = {"nodeId": entity_id} if entity_type=="node" else {"connectionId": entity_id}
                new_item.update(updates)
                data[key].append(new_item)

        data.setdefault("metadata", {})
        data["metadata"]["lastModified"] = datetime.datetime.utcnow().isoformat() + "Z"

        with open(savefile_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        if self.signal_hub: self.signal_hub.emit("file_save", {"path": str(savefile_path)})
        self.update_index()
        if self.signal_hub:
            self.signal_hub.emit("project_update", {
                "project_name": project_name, "entity_type": entity_type, "entity_id": entity_id,
                "updates": updates, "project_updates": project_updates
            })
        return data

    def delete_project(self, project_name):
        path = self.base_path / pr_
