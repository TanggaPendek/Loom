from pathlib import Path
import re


class ValidationError(Exception):
    pass


class Validator:

    def _require(self, payload, key):
        if key not in payload:
            raise ValidationError(f"Missing required field: '{key}'")

    def _check_type(self, payload, key, expected):
        if not isinstance(payload[key], expected):
            raise ValidationError(f"'{key}' must be {expected.__name__}")

    def _validate_name(self, name: str):
        if not isinstance(name, str):
            raise ValidationError("name must be a string")

        if not name.strip():
            raise ValidationError("name cannot be empty")

        if len(name) > 64:
            raise ValidationError("name too long")

        if not re.match(r"^[a-zA-Z0-9_\- ]+$", name):
            raise ValidationError("name contains invalid characters")

    def _validate_path(self, path: str):
        if not isinstance(path, str):
            raise ValidationError("path must be a string")

        p = Path(path)

        # block absolute paths
        if p.is_absolute():
            raise ValidationError("absolute paths are not allowed")

        # block path traversal
        if ".." in p.parts:
            raise ValidationError("path traversal is not allowed")



    def validate_node_payload(self, payload: dict):
        if not isinstance(payload, dict):
            raise ValidationError("payload must be a dict")

        self._require(payload, "nodeId")
        self._require(payload, "name")

        self._check_type(payload, "nodeId", str)
        self._validate_name(payload["name"])

        if "metadata" in payload and not isinstance(payload["metadata"], dict):
            raise ValidationError("metadata must be a dict")

        if "position" in payload:
            pos = payload["position"]
            if not isinstance(pos, dict):
                raise ValidationError("position must be a dict")

            if "x" not in pos or "y" not in pos:
                raise ValidationError("position must contain x and y")

            if not isinstance(pos["x"], (int, float)):
                raise ValidationError("position.x must be a number")

            if not isinstance(pos["y"], (int, float)):
                raise ValidationError("position.y must be a number")

    def validate_edge_payload(self, payload: dict):
        if not isinstance(payload, dict):
            raise ValidationError("payload must be a dict")

        self._require(payload, "from")
        self._require(payload, "to")

        self._check_type(payload, "from", str)
        self._check_type(payload, "to", str)

    def validate_file_payload(self, payload: dict):
        """
        Used before saving/editing local .json / .py files
        """
        if not isinstance(payload, dict):
            raise ValidationError("payload must be a dict")

        self._require(payload, "path")
        self._require(payload, "content")

        self._validate_path(payload["path"])

        if not isinstance(payload["content"], (str, dict)):
            raise ValidationError("content must be string or dict")




#UNTESTED