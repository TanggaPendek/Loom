# executor/engine/execution_manager.py
import asyncio
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional
from executor.engine.engine_signal import EngineSignalHub
from executor.engine.node_loader import NodeLoader
from executor.engine.variable_manager import VariableManager
from executor.engine.venv_manager import VenvManager


class ExecutionManager:
    """
    Executor Engine - Sequencer and Execution Logic
    Handles dynamic execution including loops and condition nodes.
    """

    def __init__(self, nodes=None, loaded_nodes=None, variable_manager=None, connections=None, signal_hub: Optional[EngineSignalHub] = None):
        self.signal_hub = signal_hub
        self.connections = connections or []
        self.stopped = False

        self.nodes = {node["nodeId"]: node for node in nodes} if nodes else {}
        self.loaded_nodes = loaded_nodes or {}
        self.var_mgr = variable_manager
        self.venv_mgr = None

        if self.nodes:
            self.dependencies = self._build_dependencies()
        else:
            self.dependencies = {}

        if signal_hub:
            signal_hub.on("engine_stop", self.on_stop_request)

    async def initialize_async(self, nodes: List[dict], nodebank_path: str, project_path: Optional[Path] = None) -> None:
        if self.signal_hub:
            self.signal_hub.emit("engine_progress", {
                "phase": "initialization",
                "status": "started",
                "message": "Initializing NodeLoader, VariableManager, and VenvManager..."
            })

        node_loader = NodeLoader(nodebank_path, self.signal_hub)
        var_mgr = VariableManager(self.signal_hub)
        venv_mgr = VenvManager(project_path, self.signal_hub) if project_path else None

        init_tasks = [node_loader.preload_nodes_async(nodes), var_mgr.init_variables_async(nodes)]
        if venv_mgr:
            init_tasks.append(venv_mgr.ensure_venv_async())

        try:
            if venv_mgr:
                loaded_nodes_result, _, _ = await asyncio.gather(*init_tasks)
            else:
                loaded_nodes_result, _ = await asyncio.gather(*init_tasks)

            self.nodes = {node["nodeId"]: node for node in nodes}
            self.loaded_nodes = loaded_nodes_result
            self.var_mgr = var_mgr
            self.venv_mgr = venv_mgr
            self.dependencies = self._build_dependencies()

            if self.signal_hub:
                self.signal_hub.emit("engine_progress", {
                    "phase": "initialization",
                    "status": "completed",
                    "message": f"Initialization complete: {len(self.loaded_nodes)} nodes loaded"
                })

        except Exception as e:
            if self.signal_hub:
                self.signal_hub.emit("engine_error", {"phase": "initialization", "error": str(e)})
            raise

    def _build_dependencies(self) -> Dict[str, set]:
        dep_map = {node_id: set() for node_id in self.nodes}
        var_to_node = {conn["sourceOutput"]: conn["sourceNodeId"] for conn in self.connections}

        for node_id, node in self.nodes.items():
            for inp in node.get("input", []):
                if isinstance(inp, dict) and "var" in inp:
                    producer = var_to_node.get(inp["var"])
                    if producer:
                        dep_map[node_id].add(producer)
        return dep_map

    def on_stop_request(self, payload=None):
        print("[ExecutionManager] Stop requested")
        self.stopped = True

    async def run_async(self) -> None:
        if self.signal_hub:
            self.signal_hub.emit("engine_run", {"status": "started"})

        try:
            queue = deque()
            executed_count = 0
            max_iterations = 100_000

            # Nodes with no input vars are ready first
            for node_id, node in self.nodes.items():
                if all(not ("var" in inp) for inp in node.get("input", [])):
                    queue.append(node_id)

            while queue and executed_count < max_iterations:
                node_id = queue.popleft()
                node = self.nodes[node_id]
                func = self.loaded_nodes.get(node_id)
                if not func:
                    raise RuntimeError(f"Node function not loaded for {node_id}")

                if self.stopped:
                    if self.signal_hub:
                        self.signal_hub.emit("engine_stop", {"status": "cancelled", "completed": executed_count})
                    return

                if self.signal_hub:
                    self.signal_hub.emit("engine_node_started", {"nodeId": node_id})

                inputs = self.var_mgr.get_input(node)
                loop = asyncio.get_event_loop()
                output = await loop.run_in_executor(None, func, inputs, self.var_mgr.variables)
                self.var_mgr.set_output(node_id, output)

                if self.signal_hub:
                    self.signal_hub.emit("engine_node_finished", {"nodeId": node_id, "output": output})
                    self.signal_hub.emit("engine_progress", {
                        "phase": "execution",
                        "current": executed_count + 1,
                        "percent": 0
                    })

                executed_count += 1

                # Enqueue next nodes based on input readiness and condition
                for conn in self.connections:
                    if conn["sourceNodeId"] != node_id:
                        continue

                    next_node_id = conn["targetNodeId"]
                    next_node = self.nodes[next_node_id]

                    # Condition node routing
                    if node.get("metadata", {}).get("operation") == "condition":
                        label = conn.get("metadata", {}).get("label", "")
                        if output and "true_path" not in label:
                            continue
                        if not output and "false_path" not in label:
                            continue

                    # Check if all input vars are ready
                    all_inputs_ready = True
                    for inp in next_node.get("input", []):
                        if "var" in inp and inp["var"] not in self.var_mgr.variables:
                            all_inputs_ready = False
                            break

                    if all_inputs_ready and next_node_id not in queue:
                        queue.append(next_node_id)

            if executed_count >= max_iterations:
                raise RuntimeError("Maximum iteration limit reached; possible infinite loop")

            if self.signal_hub:
                self.signal_hub.emit("engine_stop", {"status": "finished"})

        except Exception as e:
            if self.signal_hub:
                self.signal_hub.emit("engine_error", {"error": str(e)})
            raise e

    def run_linear(self) -> None:
        if self.signal_hub:
            self.signal_hub.emit("engine_run", {"status": "started"})

        try:
            order = [n for n in self.nodes]
            for node_id in order:
                if self.stopped:
                    if self.signal_hub:
                        self.signal_hub.emit("engine_stop", {"status": "cancelled"})
                    return
                node = self.nodes[node_id]
                func = self.loaded_nodes[node_id]
                inputs = self.var_mgr.get_input(node)
                output = func(inputs, self.var_mgr.variables)
                self.var_mgr.set_output(node_id, output)
                if self.signal_hub:
                    self.signal_hub.emit("engine_node_finished", {"nodeId": node_id, "output": output})

            if self.signal_hub:
                self.signal_hub.emit("engine_stop", {"status": "finished"})
        except Exception as e:
            if self.signal_hub:
                self.signal_hub.emit("engine_error", {"error": str(e)})
            raise e
