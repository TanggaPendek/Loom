from pathlib import Path
import json
import datetime
from .validator import Validator

class NodeManager:
    def __init__(self, base_path="nodebank/custom", signal_hub=None):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.signal_hub = signal_hub
        self.validator = Validator(signal_hub=signal_hub)

        if signal_hub:
            signal_hub.on("node_add_request", self._handle_add)
            signal_hub.on("node_update_request", self._handle_update)
            signal_hub.on("node_delete_request", self._handle_delete)
            signal_hub.on("node_index_request", lambda _: self.print_node_index(Path(base_path).parent / "nodeindex.json"))

    def _handle_add(self, payload):
        try:
            self.validator.validate_node_payload(payload)
            self.add_node(payload, Path(self.base_path).parent / "nodeindex.json")
        except Exception as e:
            if self.signal_hub: self.signal_hub.emit("validation_error", {"message": str(e)})

    def _handle_update(self, payload):
        try:
            self.validator.validate_node_payload(payload)
            self.update_node(payload, Path(self.base_path).parent / "nodeindex.json")
        except Exception as e:
            if self.signal_hub: self.signal_hub.emit("validation_error", {"message": str(e)})

    def _handle_delete(self, payload):
        try:
            node_id = payload.get("nodeId")
            if not node_id:
                raise ValueError("Missing nodeId")
            self.delete_node(node_id, Path(self.base_path).parent / "nodeindex.json")
        except Exception as e:
            if self.signal_hub: self.signal_hub.emit("validation_error", {"message": str(e)})
