import os
import json
import importlib.util
import asyncio
from pathlib import Path
from typing import Dict, Optional, Any
from executor.engine.engine_signal import EngineSignalHub

CURRENT_PATH = Path(__file__).parent.parent.parent / "userdata" / "state.json"

def read_current():
    if not CURRENT_PATH.exists():
        print("[NodeLoader] current.json not found")
        return None
    with open(CURRENT_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)

class NodeLoader:
    def __init__(self, nodebank_path=None, signal_hub: Optional[EngineSignalHub] = None):
        current = read_current()
        if current and not nodebank_path:
            nodebank_path = Path(current["projectPath"]).parent / "nodebank"
        self.nodebank_path = Path(nodebank_path or os.getenv("NODEBANK_PATH", "nodebank"))
        self.loaded_nodes: Dict[str, Any] = {}
        self.signal_hub = signal_hub
        self._module_cache: Dict[str, Any] = {}

    def load_node_function(self, node: dict):
        node_id = node.get("nodeId")
        node_name = node.get("name")

        # 1️⃣ Use explicit scriptPath if provided
        if "scriptPath" in node:
            script_path = Path(node["scriptPath"])
        else:
            node_type = node.get("ref", "builtin")
            script_path = self.nodebank_path / node_type / f"{node_name}.py"

        # Normalize + validate
        script_path = script_path.resolve()

        if not script_path.exists():
            if self.signal_hub:
                self.signal_hub.emit("node_load_failed", {
                    "nodeId": node_id,
                    "name": node_name,
                    "error": f"Node script not found: {script_path}"
                })
            raise FileNotFoundError(f"Node script not found: {script_path}")

        # 2️⃣ Module cache (by absolute path, not name)
        cache_key = str(script_path)
        if cache_key in self._module_cache:
            module = self._module_cache[cache_key]
        else:
            spec = importlib.util.spec_from_file_location(
                f"node_{node_id}", script_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._module_cache[cache_key] = module

        # 3️⃣ Function resolution
        entry_fn = node.get("entryFunction", node_name)
        func = getattr(module, entry_fn, None)

        if func is None:
            if self.signal_hub:
                self.signal_hub.emit("node_load_failed", {
                    "nodeId": node_id,
                    "name": node_name,
                    "error": f"Function '{entry_fn}' not found in {script_path}"
                })
            raise AttributeError(f"Function '{entry_fn}' not found in {script_path}")

        return func


    async def _load_node_async(self, node: dict) -> tuple:
        node_id = node.get("nodeId")
        node_name = node.get("name")
        if self.signal_hub:
            self.signal_hub.emit("node_loading", {"nodeId": node_id, "name": node_name})
        try:
            loop = asyncio.get_event_loop()
            func = await loop.run_in_executor(None, self.load_node_function, node)
            if self.signal_hub:
                self.signal_hub.emit("node_loaded", {"nodeId": node_id, "name": node_name})
            return (node_id, func)
        except Exception as e:
            if self.signal_hub:
                self.signal_hub.emit("node_load_failed", {"nodeId": node_id, "name": node_name, "error": str(e)})
            print(f"[WARNING] Failed to load node {node_id}: {e}")
            return (node_id, None)

    async def preload_nodes_async(self, nodes: list) -> Dict[str, Any]:
        if self.signal_hub:
            self.signal_hub.emit("nodeloader_started", {"count": len(nodes)})
        results = await asyncio.gather(*[self._load_node_async(n) for n in nodes])
        loaded_count, failed_count = 0, 0
        for node_id, func in results:
            if func is not None:
                self.loaded_nodes[node_id] = func
                loaded_count += 1
            else:
                failed_count += 1
        if self.signal_hub:
            self.signal_hub.emit("nodeloader_completed", {"loaded_count": loaded_count, "failed_count": failed_count, "total": len(nodes)})
        print(f"[NodeLoader] Preloaded {loaded_count} nodes ({failed_count} failed).")
        return self.loaded_nodes

    def preload_nodes(self, nodes: list) -> Dict[str, Any]:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return self._preload_nodes_sync(nodes)
            else:
                return asyncio.run(self.preload_nodes_async(nodes))
        except RuntimeError:
            return self._preload_nodes_sync(nodes)

    def _preload_nodes_sync(self, nodes: list) -> Dict[str, Any]:
        loaded_count, failed_count = 0, 0
        for node in nodes:
            node_id = node.get("nodeId")
            try:
                func = self.load_node_function(node)
                self.loaded_nodes[node_id] = func
                loaded_count += 1
                if self.signal_hub:
                    self.signal_hub.emit("node_loaded", {"nodeId": node_id, "name": node.get("name")})
            except Exception as e:
                failed_count += 1
                print(f"[WARNING] Failed to load node {node_id}: {e}")
        if self.signal_hub:
            self.signal_hub.emit("nodeloader_completed", {"loaded_count": loaded_count, "failed_count": failed_count, "total": len(nodes)})
        print(f"[NodeLoader] Preloaded {loaded_count} nodes ({failed_count} failed).")
        return self.loaded_nodes
