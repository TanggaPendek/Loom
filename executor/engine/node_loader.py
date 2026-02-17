import os
import json
import importlib.util
import asyncio
import inspect
from pathlib import Path
from typing import Dict, Optional, Any
from executor.engine.engine_signal import EngineSignalHub

CURRENT_PATH = Path(__file__).parent.parent.parent / "userdata" / "state.json"

def read_current():
    if not CURRENT_PATH.exists():
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

        # Resolve script path
        if "scriptPath" in node:
            script_path = Path(node["scriptPath"])
        else:
            node_type = node.get("ref", "builtin")
            script_path = self.nodebank_path / node_type / f"{node_name}.py"

        script_path = script_path.resolve()
        if not script_path.exists():
            raise FileNotFoundError(f"Node script not found: {script_path}")

        # Module cache
        cache_key = str(script_path)
        if cache_key in self._module_cache:
            module = self._module_cache[cache_key]
        else:
            spec = importlib.util.spec_from_file_location(f"node_{node_id}", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._module_cache[cache_key] = module

        # Resolve function
        entry_fn = node.get("entryFunction", node_name)
        func = getattr(module, entry_fn, None)
        if func is None:
            raise AttributeError(f"Function '{entry_fn}' not found in {script_path}")

        # 🔑 NEW: Function metadata
        sig = inspect.signature(func)
        func._param_count = len(sig.parameters)

        # Optional: hint return arity (non-binding)
        func._returns_tuple = True  # engine will normalize anyway

        return func

    async def _load_node_async(self, node: dict):
        node_id = node["nodeId"]
        try:
            loop = asyncio.get_event_loop()
            func = await loop.run_in_executor(None, self.load_node_function, node)
            return node_id, func
        except Exception as e:
            print(f"[NodeLoader] Failed to load node {node_id}: {e}")
            return node_id, None

    async def preload_nodes_async(self, nodes: list):
        results = await asyncio.gather(*[self._load_node_async(n) for n in nodes])
        for node_id, func in results:
            if func:
                self.loaded_nodes[node_id] = func
        return self.loaded_nodes

    def preload_nodes(self, nodes: list):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return self._preload_nodes_sync(nodes)
            return asyncio.run(self.preload_nodes_async(nodes))
        except RuntimeError:
            return self._preload_nodes_sync(nodes)

    def _preload_nodes_sync(self, nodes: list):
        for node in nodes:
            try:
                func = self.load_node_function(node)
                self.loaded_nodes[node["nodeId"]] = func
            except Exception as e:
                print(f"[NodeLoader] Failed to load node {node['nodeId']}: {e}")
        return self.loaded_nodes
