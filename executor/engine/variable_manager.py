import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from executor.engine.engine_signal import EngineSignalHub

CURRENT_PATH = Path(__file__).parent.parent.parent / "userdata" / "current.json"

def read_current():
    if not CURRENT_PATH.exists():
        print("[VarManager] current.json not found")
        return None
    with open(CURRENT_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)

class VariableManager:
    def __init__(self, signal_hub: Optional[EngineSignalHub] = None):
        self.variables: Dict[str, Any] = {}
        self.node_output_map: Dict[str, List[str]] = {}
        self.signal_hub = signal_hub

    async def init_variables_async(self, nodes: list) -> None:
        if self.signal_hub:
            self.signal_hub.emit("varmanager_started", {"node_count": len(nodes)})
        await asyncio.sleep(0)
        for node in nodes:
            node_id = node["nodeId"]
            outputs = node.get("output", [])
            self.node_output_map[node_id] = outputs
            defaults = node.get("metadata", {}).get("defaults", {})
            for out_var in outputs:
                self.variables[out_var] = defaults.get(out_var, None)
        if self.signal_hub:
            self.signal_hub.emit("varmanager_initialized", {"variable_count": len(self.variables), "node_count": len(nodes)})

    def init_variables(self, nodes: list) -> None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._init_variables_sync(nodes)
            else:
                asyncio.run(self.init_variables_async(nodes))
        except RuntimeError:
            self._init_variables_sync(nodes)

    def _init_variables_sync(self, nodes: list) -> None:
        for node in nodes:
            node_id = node["nodeId"]
            outputs = node.get("output", [])
            self.node_output_map[node_id] = outputs
            defaults = node.get("metadata", {}).get("defaults", {})
            for out_var in outputs:
                self.variables[out_var] = defaults.get(out_var, None)
        if self.signal_hub:
            self.signal_hub.emit("varmanager_initialized", {"variable_count": len(self.variables), "node_count": len(nodes)})

    def get_input(self, node: dict) -> List[Any]:
        values = []
        for inp in node.get("input", []):
            if isinstance(inp, dict):
                if "var" in inp:
                    values.append(self.variables.get(inp["var"]))
                elif "value" in inp:
                    values.append(inp["value"])
            else:
                raise ValueError(f"Legacy input format not supported: {inp}")
        return values

    def set_output(self, node_id: str, output_values: Any) -> None:
        outputs = self.node_output_map.get(node_id, [])
        if not outputs:
            return
        if not isinstance(output_values, (list, tuple)):
            output_values = [output_values]
        if len(outputs) != len(output_values):
            raise ValueError(f"Output mismatch for node {node_id}: expected {len(outputs)} got {len(output_values)}")
        for var_name, val in zip(outputs, output_values):
            old_value = self.variables.get(var_name)
            self.variables[var_name] = val
            if self.signal_hub and old_value != val:
                self.signal_hub.emit("variable_set", {"var_name": var_name, "old_value": old_value, "new_value": val, "node_id": node_id})

    async def init_from_current_project_async(self):
        current = read_current()
        if not current:
            print("[VarManager] No active project found")
            return
        graph_path = Path(current["projectPath"])
        if not graph_path.exists():
            print(f"[VarManager] Graph file not found: {graph_path}")
            return
        with open(graph_path, "r", encoding="utf-8-sig") as f:
            project_json = json.load(f)
        nodes = project_json.get("nodes", [])
        await self.init_variables_async(nodes)
