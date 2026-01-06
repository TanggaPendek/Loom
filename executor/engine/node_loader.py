# executor/engine/node_loader.py
import os
import importlib.util
import asyncio
from pathlib import Path
from typing import Dict, Optional, Any
from executor.engine.engine_signal import EngineSignalHub



class NodeLoader:
    def __init__(self, nodebank_path=None, signal_hub: Optional[EngineSignalHub] = None):
        """
        Initialize NodeLoader with signal support.
        
        Args:
            nodebank_path: Path to nodebank directory
            signal_hub: Optional EngineSignalHub for emitting signals
        """
        self.nodebank_path = Path(nodebank_path or os.getenv("NODEBANK_PATH", "nodebank"))
        self.loaded_nodes: Dict[str, Any] = {}  # nodeId -> function
        self.signal_hub = signal_hub
        self._module_cache: Dict[str, Any] = {}  # Cache loaded modules

    def load_node_function(self, node: dict):
        """
        Load a node script from nodebank dynamically (synchronous).
        
        Args:
            node: Dictionary from the JSON with 'ref' and 'name' keys
            
        Returns:
            Loaded function
            
        Raises:
            FileNotFoundError: If script not found
            AttributeError: If function not found in module
        """
        node_type = node.get("ref", "builtin")  # folder: builtin or custom
        node_name = node.get("name")            # script & function name
        node_id = node.get("nodeId", node_name)

        script_path = self.nodebank_path / node_type / f"{node_name}.py"
        if not script_path.exists():
            error_msg = f"Node script not found: {script_path}"
            if self.signal_hub:
                self.signal_hub.emit("node_load_failed", {
                    "nodeId": node_id,
                    "name": node_name,
                    "error": error_msg
                })
            raise FileNotFoundError(f"\n{error_msg}")

        # Check cache first
        cache_key = str(script_path)
        if cache_key in self._module_cache:
            module = self._module_cache[cache_key]
        else:
            # Load module
            spec = importlib.util.spec_from_file_location(node_name, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._module_cache[cache_key] = module

        func = getattr(module, node_name, None)
        if func is None:
            error_msg = f"Function '{node_name}' not found in {script_path}"
            if self.signal_hub:
                self.signal_hub.emit("node_load_failed", {
                    "nodeId": node_id,
                    "name": node_name,
                    "error": error_msg
                })
            raise AttributeError(f"\n{error_msg}")

        return func

    async def _load_node_async(self, node: dict) -> tuple:
        """
        Load a single node asynchronously.
        
        Args:
            node: Node dictionary
            
        Returns:
            Tuple of (node_id, function) or (node_id, None) on error
        """
        node_id = node.get("nodeId")
        node_name = node.get("name")
        
        if self.signal_hub:
            self.signal_hub.emit("node_loading", {
                "nodeId": node_id,
                "name": node_name
            })
        
        try:
            # Run blocking load in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            func = await loop.run_in_executor(None, self.load_node_function, node)
            
            if self.signal_hub:
                self.signal_hub.emit("node_loaded", {
                    "nodeId": node_id,
                    "name": node_name
                })
            
            return (node_id, func)
        except Exception as e:
            if self.signal_hub:
                self.signal_hub.emit("node_load_failed", {
                    "nodeId": node_id,
                    "name": node_name,
                    "error": str(e)
                })
            print(f"\n[WARNING] Failed to load node {node_id} ({node.get('ref', 'builtin')}): {e}")
            return (node_id, None)

    async def preload_nodes_async(self, nodes: list) -> Dict[str, Any]:
        """
        Preload all nodes from project JSON asynchronously and concurrently.
        
        Args:
            nodes: List of node dicts
            
        Returns:
            Dictionary mapping nodeId -> function
        """
        if self.signal_hub:
            self.signal_hub.emit("nodeloader_started", {"count": len(nodes)})
        
        # Load all nodes concurrently
        tasks = [self._load_node_async(node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Build loaded_nodes dict
        loaded_count = 0
        failed_count = 0
        for node_id, func in results:
            if func is not None:
                self.loaded_nodes[node_id] = func
                loaded_count += 1
            else:
                failed_count += 1
        
        if self.signal_hub:
            self.signal_hub.emit("nodeloader_completed", {
                "loaded_count": loaded_count,
                "failed_count": failed_count,
                "total": len(nodes)
            })
        
        print(f"\n[NodeLoader] Preloaded {loaded_count} nodes ({failed_count} failed).")
        return self.loaded_nodes

    def preload_nodes(self, nodes: list) -> Dict[str, Any]:
        """
        Preload all nodes from project JSON (synchronous wrapper).
        
        This is a synchronous wrapper around preload_nodes_async() for
        backward compatibility. Prefer using preload_nodes_async() directly
        in async contexts.
        
        Args:
            nodes: List of node dicts
            
        Returns:
            Dictionary mapping nodeId -> function
        """
        # Try to run async version if event loop exists
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Can't use asyncio.run in a running loop, fall back to sync
                return self._preload_nodes_sync(nodes)
            else:
                return asyncio.run(self.preload_nodes_async(nodes))
        except RuntimeError:
            # No event loop, use sync version
            return self._preload_nodes_sync(nodes)
    
    def _preload_nodes_sync(self, nodes: list) -> Dict[str, Any]:
        """
        Synchronous fallback for preload_nodes (legacy).
        
        Args:
            nodes: List of node dicts
            
        Returns:
            Dictionary mapping nodeId -> function
        """
        if self.signal_hub:
            self.signal_hub.emit("nodeloader_started", {"count": len(nodes)})
        
        loaded_count = 0
        failed_count = 0
        
        for node in nodes:
            node_id = node.get("nodeId")
            try:
                func = self.load_node_function(node)
                self.loaded_nodes[node_id] = func
                loaded_count += 1
                
                if self.signal_hub:
                    self.signal_hub.emit("node_loaded", {
                        "nodeId": node_id,
                        "name": node.get("name")
                    })
            except Exception as e:
                failed_count += 1
                print(f"\n[WARNING] Failed to load node {node_id} ({node.get('ref', 'builtin')}): {e}")
        
        if self.signal_hub:
            self.signal_hub.emit("nodeloader_completed", {
                "loaded_count": loaded_count,
                "failed_count": failed_count,
                "total": len(nodes)
            })
        
        print(f"\n[NodeLoader] Preloaded {loaded_count} nodes ({failed_count} failed).")
        return self.loaded_nodes