import json
import shutil
import datetime
from pathlib import Path
from .storage_manager import StorageManager

class ProjectManager:
    def __init__(self, base_path="userdata", signal_hub=None):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.signal_hub = signal_hub
        StorageManager.init_storage()

        if self.signal_hub:
            # Standard Request Handlers
            self.signal_hub.on("current_request", lambda _: self.signal_hub.emit("current_response", self.read_current()))
            self.signal_hub.on("project_create_request", lambda p: self.init_project(
                project_name=p.get("projectName"),
                description=p.get("description"),
                author=p.get("author", "author")
            ))
            self.signal_hub.on("project_update_request", lambda p: self.update_project(**p))
            self.signal_hub.on("project_delete_request", lambda p: self.delete_project(p.get("projectName")))
            self.signal_hub.on("project_change_request", lambda p: self.change_project(p.get("projectId")))

    # ===== State Management =====

    def write_current(self, project_obj):
        """Updates state.json with the active project data.
        
        Note: state.json IS the active project - no nested 'active_project' field.
        """
        if not project_obj:
            return
        
        # state.json directly contains the project data
        StorageManager.save_state(project_obj)
        
        if self.signal_hub:
            self.signal_hub.emit("current_updated", project_obj)

    def read_current(self):
        """Retrieves the active project from state.json.
        
        Returns the entire state.json content which IS the active project.
        """
        return StorageManager.get_state()

    # ===== Project Operations =====

    def init_project(self, project_name=None, description=None, author="author"):
        folder_count = len([d for d in self.base_path.iterdir() if d.is_dir()]) + 1
        project_name = project_name or f"Project_{folder_count}"
        
        project_path = self.base_path / project_name
        # ... (Keep your existing conflict resolution logic here) ...

        try:
            project_path.mkdir(parents=True, exist_ok=True)
            savefile_path = project_path / "savefile.json"

            # 1. Create the project data structure
            project_id = f"proj_{folder_count:03d}_{datetime.datetime.now().strftime('%M%S')}"
            project_data = {
                "projectId": project_id,
                "projectName": project_name,
                "projectPath": str(savefile_path),
                "metadata": {
                    "author": author,
                    "description": description or f"description for {project_name}",
                    "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
                    "lastModified": datetime.datetime.utcnow().isoformat() + "Z"
                },
                "nodes": [],
                "connections": []
            }

            # 2. Write the savefile.json to the new folder
            with open(savefile_path, "w", encoding="utf-8-sig") as f:
                json.dump(project_data, f, indent=4)

            # 3. 🔑 UPDATE FOLDER INDEX FIRST (so change_project can find it)
            index_path = self.base_path / "folderindex.json"
            index = []
            if index_path.exists():
                with open(index_path, "r", encoding="utf-8") as f:
                    index = json.load(f)
            
            # Add new project to index
            index.append({
                "projectId": project_id,
                "projectName": project_name,
                "projectPath": str(savefile_path)
            })
            
            with open(index_path, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=4)

            # 4. Now call change_project (it can find the project in index)
            full_loaded_data = self.change_project(project_id)

            if self.signal_hub:
                self.signal_hub.emit("project_index_update_required")
            
            return {"status": "ok", "project": full_loaded_data or project_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def update_project(self, project_name: str, entity_type: str = None, 
                       entity_id: str = None, updates: dict = None, 
                       project_updates: dict = None):
        """Updates existing project data (metadata or node/connection data)."""
        savefile_path = self.base_path / project_name / "savefile.json"
        if not savefile_path.exists(): 
            return {"status": "error", "message": "Project not found"}

        with open(savefile_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        # 1. Handle Project-level Metadata updates
        if project_updates:
            if "projectName" in project_updates:
                data["projectName"] = project_updates["projectName"]
            if "description" in project_updates:
                data["metadata"]["description"] = project_updates["description"]
            if "author" in project_updates:
                data["metadata"]["author"] = project_updates["author"]

        # 2. Handle Node/Connection entity updates
        elif entity_type and entity_id:
            key = "nodes" if entity_type == "node" else "connections"
            id_key = "nodeId" if entity_type == "node" else "connectionId"
            
            found = False
            for item in data[key]:
                if item.get(id_key) == entity_id:
                    item.update(updates or {})
                    found = True
                    break
            
            if not found:
                new_item = {id_key: entity_id}
                new_item.update(updates or {})
                data[key].append(new_item)

        data["metadata"]["lastModified"] = datetime.datetime.utcnow().isoformat() + "Z"

        with open(savefile_path, "w", encoding="utf-8-sig") as f:
            json.dump(data, f, indent=4)

        # If we just updated the active project, sync the state
        current = self.read_current()
        if current and current.get("projectId") == data.get("projectId"):
            self.write_current(data)

        if self.signal_hub:
            self.signal_hub.emit("project_index_update_required")
            
        return {"status": "success", "data": data}

    def change_project(self, project_id: str):
        """Switches the active project based on ID (searches via index)."""
        index_path = self.base_path / "folderindex.json"
        if not index_path.exists(): return
        
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
            
        project_meta = next((p for p in index if p["projectId"] == project_id), None)
        if project_meta:
            # Read full file to get the nodes/connections
            full_path = Path(project_meta["projectPath"])
            if full_path.exists():
                with open(full_path, "r", encoding="utf-8-sig") as f:
                    full_data = json.load(f)
                    self.write_current(full_data)
                    return full_data
        return None

    def delete_project(self, project_name: str):
        """Deletes project folder and clears active state."""
        if not project_name:
            return {"status": "error", "message": "No project name provided"}

        project_path = self.base_path / project_name
        if project_path.exists():
            shutil.rmtree(project_path)
            
            # Check if deleted project was active, if so clear state
            current = self.read_current()
            if current and current.get("projectName") == project_name:
                # Clear state.json (set to empty project)
                empty_state = {
                    "projectId": None,
                    "projectName": None,
                    "projectPath": None
                }
                StorageManager.save_state(empty_state)
            
            if self.signal_hub:
                self.signal_hub.emit("project_index_update_required")
            
            return {"status": "ok", "message": f"Project {project_name} deleted"}
        
        return {"status": "error", "message": "Project folder not found"}