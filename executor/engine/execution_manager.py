import asyncio
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional
from executor.engine.node_loader import NodeLoader
from executor.engine.variable_manager import VariableManager

class ExecutionManager:
    def __init__(self, nodes=None, connections=None, signal_hub=None):
        self.signal_hub = signal_hub
        self.connections = connections or []
        self.stopped = False
        self.nodes = {node["nodeId"]: node for node in nodes} if nodes else {}
        self.loaded_nodes = {}
        self.var_mgr = None
        
        if signal_hub:
            signal_hub.on("engine_stop", self.on_stop_request)

    async def initialize_async(self, nodes, nodebank_path, project_path=None):
        """Initializes the loader and variable manager concurrently."""
        node_loader = NodeLoader(nodebank_path, self.signal_hub)
        var_mgr = VariableManager(self.signal_hub)
        
        # Preload custom python nodes and initialize the variable state
        tasks = [
            node_loader.preload_nodes_async(nodes), 
            var_mgr.init_variables_async(nodes)
        ]
        
        results = await asyncio.gather(*tasks)
        self.loaded_nodes = results[0]
        self.var_mgr = var_mgr
        self.nodes = {node["nodeId"]: node for node in nodes}

    def on_stop_request(self, payload=None):
        self.stopped = True

    async def run_async(self) -> None:
        """Executes the graph based on node connections and logic."""
        if self.signal_hub:
            self.signal_hub.emit("engine_run", {"status": "started"})

        try:
            queue = deque()
            executed_count = 0
            
            # Step 1: Find Entry Points (Nodes with no variable inputs)
            for node_id, node in self.nodes.items():
                if all(not ("var" in inp) for inp in node.get("input", [])):
                    queue.append(node_id)

            # Step 2: Main Execution Loop
            while queue and executed_count < 10000:
                if self.stopped: break
                
                node_id = queue.popleft()
                node = self.nodes[node_id]
                func = self.loaded_nodes.get(node_id)

                if not func:
                    print(f"[ENGINE ERROR] No function loaded for node: {node_id}")
                    continue

                if self.signal_hub:
                    self.signal_hub.emit("engine_node_started", {"nodeId": node_id})

                # Fetch data and run logic
                inputs = self.var_mgr.get_input(node)
                output = await asyncio.to_thread(func, inputs, self.var_mgr.variables)
                
                # Update State
                self.var_mgr.set_output(node_id, output)
                executed_count += 1

                if self.signal_hub:
                    self.signal_hub.emit("engine_node_finished", {"nodeId": node_id, "output": output})

                # Step 3: Reactive Routing with Conditional Logic
                for conn in self.connections:
                    if conn["sourceNodeId"] != node_id:
                        continue

                    target_id = conn["targetNodeId"]
                    label = str(conn.get("metadata", {}).get("label", "")).lower()

                    # Logic Check for Condition Nodes
                    if node.get("metadata", {}).get("operation") == "condition":
                        is_true = bool(output)
                        if is_true and "true" not in label:
                            continue
                        if not is_true and "false" not in label:
                            continue
                    
                    queue.append(target_id)

            if self.signal_hub:
                self.signal_hub.emit("engine_stop", {"status": "finished"})
                
        except Exception as e:
            if self.signal_hub:
                self.signal_hub.emit("engine_error", {"error": str(e)})
            raise e