import asyncio
from collections import defaultdict, deque
from typing import Dict, Any, Tuple, Optional

from executor.engine.engine_signal import EngineSignalHub
from executor.engine.node_loader import NodeLoader
from executor.utils.node_logger import init_logger

class ExecutionManager:
    def __init__(self, nodes, connections, signal_hub: Optional[EngineSignalHub] = None):
        self.nodes: Dict[str, dict] = {}
        self.connections = connections
        self.signal_hub = signal_hub
        
        # Optional log manager passed from main_engine
        self.log_manager = None
        self.project_id = None

        # Runtime state
        self.functions: Dict[str, Any] = {}
        self.input_buckets: Dict[Tuple[str, int], Any] = {}
        self.ready_queue = deque()

        # Graph structure
        self.incoming_count = defaultdict(int)
        self.outgoing = defaultdict(list)

    def _parse_value(self, value: Any, value_type: str = None) -> Any:
        """Convert string values to appropriate types based on type hint"""
        if value is None:
            return None
        
        # If already correct type, return as-is
        if not isinstance(value, str):
            return value
            
        # Try to infer or use explicit type
        if value_type:
            try:
                if value_type in ("number", "float"):
                    return float(value)
                elif value_type in ("integer", "int"):
                    return int(value)
                elif value_type == "boolean":
                    return value.lower() in ("true", "1", "yes")
                elif value_type == "string":
                    return str(value)
            except (ValueError, AttributeError):
                pass
        
        # Auto-detect numeric types
        try:
            # Try int first
            if '.' not in value:
                return int(value)
            # Then float
            return float(value)
        except (ValueError, AttributeError):
            pass
        
        # Boolean check
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        
        # Default to string
        return value

    async def initialize_async(self, nodes: list, nodebank_path=None, project_path=None,
                              log_manager=None, project_id=None):
        """
        Async initialization with optional logging support.
        
        Args:
            nodes: List of node dictionaries
            nodebank_path: Path to nodebank directory
            project_path: Path to project directory
            log_manager: Optional LogManager for per-node logging
            project_id: Optional project ID for logging
        """
        # Store log manager and project_id for use in run_async
        self.log_manager = log_manager
        self.project_id = project_id
        
        # Load all node functions
        loader = NodeLoader(nodebank_path=nodebank_path, signal_hub=self.signal_hub)
        self.functions = await loader.preload_nodes_async(nodes)

        # Store node definitions
        for node in nodes:
            self.nodes[node["nodeId"]] = node

        # Pre-fill input buckets with defaults (NOW WITH TYPE CONVERSION)
        for node_id, node in self.nodes.items():
            for i, inp in enumerate(node.get("input", [])):
                raw_value = inp.get("value", None)
                value_type = inp.get("type", None)  # Get type hint if available
                
                # Parse the value to correct type
                parsed_value = self._parse_value(raw_value, value_type)
                self.input_buckets[(node_id, i)] = parsed_value

        # Build graph connections
        for conn in self.connections:
            src = conn["sourceNodeId"]
            tgt = conn["targetNodeId"]
            src_port = conn.get("sourcePort", 0)
            tgt_port = conn.get("targetPort", 0)
            self.outgoing[src].append((src_port, tgt, tgt_port))
            self.incoming_count[tgt] += 1

        # Entry nodes = no incoming connections
        for node_id in self.nodes:
            if self.incoming_count[node_id] == 0:
                self.ready_queue.append(node_id)

    async def run_async(self):
        # Keep track of counts locally so we don't mutate the original structure
        remaining_inbound = self.incoming_count.copy()

        while self.ready_queue:
            node_id = self.ready_queue.popleft()
            func = self.functions.get(node_id)
            
            if not func:
                print(f"[ExecutionManager] Node {node_id} skipped: function not loaded")
                continue

            # 1. Initialize Logger for this specific node context
            # This allows log_print() inside the node to write to the correct project folder
            from executor.utils.node_logger import init_logger
            init_logger(node_id=node_id)

            # 2. Gather inputs
            inputs = []
            i = 0
            while (node_id, i) in self.input_buckets:
                inputs.append(self.input_buckets[(node_id, i)])
                i += 1

            # 3. Execute node
            try:
                result = func(*inputs)
                if asyncio.iscoroutine(result):
                    result = await result
            except Exception as e:
                print(f"[ExecutionManager] Node {node_id} failed: {e}")
                import traceback
                traceback.print_exc()
                continue

            # 4. Normalize outputs
            if not isinstance(result, (list, tuple)):
                result = [result]

            # 5. Route outputs and manage the queue
            for src_port, tgt_id, tgt_port in self.outgoing.get(node_id, []):
                if src_port >= len(result):
                    continue
                
                # Pass the data to the target port
                value = result[src_port]
                self.input_buckets[(tgt_id, tgt_port)] = value
                
                # 🔑 FIX: Only queue target node if ALL its inputs are ready
                remaining_inbound[tgt_id] -= 1
                if remaining_inbound[tgt_id] <= 0:
                    self.ready_queue.append(tgt_id)

            # 6. Signal completion
            if self.signal_hub:
                self.signal_hub.emit("node_executed", {"nodeId": node_id, "output": result})