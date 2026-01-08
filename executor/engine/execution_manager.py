import asyncio
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional
from executor.engine.node_loader import NodeLoader
from executor.engine.variable_manager import VariableManager
from executor.engine.venv_handlers import VenvManager

class ExecutionManager:
    def __init__(self, nodes=None, loaded_nodes=None, variable_manager=None, connections=None, signal_hub=None):
        self.signal_hub = signal_hub
        self.connections = connections or []
        self.stopped = False
        self.nodes = {node["nodeId"]: node for node in nodes} if nodes else {}
        self.loaded_nodes = loaded_nodes or {}
        self.var_mgr = variable_manager
        self.venv_mgr = None
        if signal_hub:
            signal_hub.on("engine_stop", self.on_stop_request)

    async def initialize_async(self, nodes, nodebank_path, project_path=None):
        node_loader = NodeLoader(nodebank_path, self.signal_hub)
        var_mgr = VariableManager(self.signal_hub)
        venv_mgr = VenvManager(project_path, self.signal_hub) if project_path else None
        
        tasks = [node_loader.preload_nodes_async(nodes), var_mgr.init_variables_async(nodes)]
        if venv_mgr: tasks.append(venv_mgr.ensure_venv_async())
        
        results = await asyncio.gather(*tasks)
        self.loaded_nodes, self.var_mgr, self.venv_mgr = results[0], var_mgr, venv_mgr
        self.nodes = {node["nodeId"]: node for node in nodes}

    def on_stop_request(self, payload=None):
        self.stopped = True

    async def run_async(self) -> None:
        if self.signal_hub:
            self.signal_hub.emit("engine_run", {"status": "started"})

        try:
            queue = deque()
            executed_count = 0
            max_iterations = 10000 

            # Step 1: Entry Points (Nodes with no variable inputs)
            for node_id, node in self.nodes.items():
                if all(not ("var" in inp) for inp in node.get("input", [])):
                    queue.append(node_id)

            # Step 2: Continuous Execution Loop
            while queue and executed_count < max_iterations:
                if self.stopped: break

                node_id = queue.popleft()
                node = self.nodes[node_id]
                func = self.loaded_nodes.get(node_id)

                if self.signal_hub:
                    self.signal_hub.emit("engine_node_started", {"nodeId": node_id})

                # Always fetch fresh inputs from the VariableManager
                inputs = self.var_mgr.get_input(node)
                
                # Execute node logic
                loop = asyncio.get_event_loop()
                output = await loop.run_in_executor(None, func, inputs, self.var_mgr.variables)
                
                # Update global state
                self.var_mgr.set_output(node_id, output)
                executed_count += 1

                if self.signal_hub:
                    self.signal_hub.emit("engine_node_finished", {"nodeId": node_id, "output": output})
                    self.signal_hub.emit("engine_progress", {"phase": "execution", "current": executed_count, "percent": 0})

                # Step 3: Reactive Routing (The fix for your loop)
                for conn in self.connections:
                    if conn["sourceNodeId"] != node_id:
                        continue

                    target_id = conn["targetNodeId"]
                    label = conn.get("metadata", {}).get("label", "").lower()

                    # Handle Condition Branching
                    if node.get("metadata", {}).get("operation") == "condition":
                        is_true = bool(output)
                        if is_true and "true" not in label: continue
                        if not is_true and "false" not in label: continue

                    # PUSH to queue: We don't check if it ran before. 
                    # If the connection triggers, the target MUST run.
                    queue.append(target_id)

            if self.signal_hub:
                self.signal_hub.emit("engine_stop", {"status": "finished"})

        except Exception as e:
            if self.signal_hub:
                self.signal_hub.emit("engine_error", {"error": str(e)})
            raise e