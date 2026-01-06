# modules/validator.py
from pathlib import Path
import re

class ValidationError(Exception):
    pass

class Validator:
    def __init__(self, signal_hub=None):
        self.signal_hub = signal_hub

    def _require(self, payload, key):
        if key not in payload:
            raise ValidationError(f"Missing required field: '{key}'")

    def _check_type(self, payload, key, expected):
        if not isinstance(payload[key], expected):
            raise ValidationError(f"'{key}' must be {expected.__name__}")

    def _validate_name(self, name: str):
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("name must be non-empty string")
        if len(name) > 64:
            raise ValidationError("name too long")
        if not re.match(r"^[a-zA-Z0-9_\- ]+$", name):
            raise ValidationError("name contains invalid characters")

    def _validate_path(self, path: str):
        if not isinstance(path, str):
            raise ValidationError("path must be string")
        p = Path(path)
        if p.is_absolute() or ".." in p.parts:
            raise ValidationError("invalid path (absolute or traversal not allowed)")

    # ===== Validators =====
    def validate_project_payload(self, payload: dict):
        if not isinstance(payload, dict):
            raise ValidationError("payload must be dict")
        if "projectName" in payload:
            self._validate_name(payload["projectName"])

    def validate_node_payload(self, payload: dict):
        if not isinstance(payload, dict):
            raise ValidationError("payload must be dict")
        self._require(payload, "nodeId")
        self._require(payload, "name")
        self._check_type(payload, "nodeId", str)
        self._validate_name(payload["name"])
        if "metadata" in payload and not isinstance(payload["metadata"], dict):
            raise ValidationError("metadata must be dict")
        if "position" in payload:
            pos = payload["position"]
            if not isinstance(pos, dict) or "x" not in pos or "y" not in pos:
                raise ValidationError("position must contain x and y")
            if not isinstance(pos["x"], (int, float)) or not isinstance(pos["y"], (int, float)):
                raise ValidationError("position x/y must be numbers")
