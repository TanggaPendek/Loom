from pathlib import Path
import json

class NodeManager:
    def __init__(self, base_path="nodebank/custom", signal_hub=None):
        # We target the 'custom' folder for user-created nodes
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.signal_hub = signal_hub

        if signal_hub:
            # Registering CRUD requests
            self.signal_hub.on("node_create_request", self._handle_add)
            self.signal_hub.on("node_update_request", self._handle_update)
            self.signal_hub.on("node_delete_request", self._handle_delete)

    def _handle_add(self, payload):
        """Saves node data to a file (JSON for metadata or .py for logic)."""
        node_id = payload.get("nodeId")
        if not node_id: 
            return

        # Determine if we are saving a script or metadata
        # If 'code' is in payload, save as .py, otherwise .json
        is_script = "code" in payload
        extension = ".py" if is_script else ".json"
        file_path = self.base_path / f"{node_id}{extension}"

        try:
            if is_script:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(payload.get("code", ""))
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=4)
            
            # 🚀 CRITICAL: Tell IndexService to re-scan
            if self.signal_hub:
                self.signal_hub.emit("node_index_update_required", {"nodeId": node_id})
                
        except Exception as e:
            print(f"[NODE MANAGER] Save Error: {e}")

    def _handle_update(self, payload):
        """In this file-based system, update is a simple overwrite."""
        self._handle_add(payload) 

    def _handle_delete(self, payload):
        """Deletes the node file and triggers an index refresh."""
        node_id = payload.get("nodeId")
        
        # Check for both .py and .json versions to be safe
        deleted = False
        for ext in [".json", ".py"]:
            file_path = self.base_path / f"{node_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                deleted = True
        
        if deleted and self.signal_hub:
            self.signal_hub.emit("node_index_update_required", {"nodeId": node_id})