# executor/engine/variable_manager.py
import asyncio
from typing import Dict, List, Any, Optional
from executor.engine.engine_signal import EngineSignalHub



class VariableManager:
    def __init__(self, signal_hub: Optional[EngineSignalHub] = None):
        """
        Initialize VariableManager.
        
        Args:
            signal_hub: Optional EngineSignalHub for emitting signals
        """
        self.variables: Dict[str, Any] = {}  # variable_name -> value
        self.node_output_map: Dict[str, List[str]] = {}  # nodeId -> list of output variable names
        self.signal_hub = signal_hub

    async def init_variables_async(self, nodes: list) -> None:
        """
        Initialize variables for all nodes asynchronously.
        
        Primitive inputs are pre-set if provided in metadata (applied to outputs if needed).
        This is async-ready for future enhancements (e.g., loading defaults from files).
        
        Args:
            nodes: List of node dictionaries
        """
        if self.signal_hub:
            self.signal_hub.emit("varmanager_started", {"node_count": len(nodes)})
        
        # Currently synchronous but wrapped in async for future extensibility
        await asyncio.sleep(0)  # Yield control to event loop
        
        for node in nodes:
            node_id = node["nodeId"]

            # Initialize outputs
            outputs = node.get("output", [])
            self.node_output_map[node_id] = outputs

            metadata = node.get("metadata", {})
            defaults = metadata.get("defaults", {})

            for out_var in outputs:
                # Assign default if exists, else None
                self.variables[out_var] = defaults.get(out_var, None)

            # Initialize primitive inputs if defaults exist for input names
            # Only for literal default values, skip actual input descriptors
            for inp in node.get("input", []):
                if isinstance(inp, dict) and "var" not in inp and "value" in inp:
                    # One-off literal default for this node, stored in a temp var name if needed
                    # Optional: skip, since literals don't need global storage
                    pass
        
        variable_count = len(self.variables)
        if self.signal_hub:
            self.signal_hub.emit("varmanager_initialized", {
                "variable_count": variable_count,
                "node_count": len(nodes)
            })

    def init_variables(self, nodes: list) -> None:
        """
        Initialize variables for all nodes (synchronous wrapper).
        
        This is a synchronous wrapper around init_variables_async() for
        backward compatibility.
        
        Args:
            nodes: List of node dictionaries
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Can't use asyncio.run in a running loop, call sync version
                self._init_variables_sync(nodes)
            else:
                asyncio.run(self.init_variables_async(nodes))
        except RuntimeError:
            # No event loop
            self._init_variables_sync(nodes)
    
    def _init_variables_sync(self, nodes: list) -> None:
        """Synchronous initialization (legacy)."""
        if self.signal_hub:
            self.signal_hub.emit("varmanager_started", {"node_count": len(nodes)})
        
        for node in nodes:
            node_id = node["nodeId"]

            # Initialize outputs
            outputs = node.get("output", [])
            self.node_output_map[node_id] = outputs

            metadata = node.get("metadata", {})
            defaults = metadata.get("defaults", {})

            for out_var in outputs:
                # Assign default if exists, else None
                self.variables[out_var] = defaults.get(out_var, None)

            # Initialize primitive inputs if defaults exist for input names
            for inp in node.get("input", []):
                if isinstance(inp, dict) and "var" not in inp and "value" in inp:
                    pass
        
        variable_count = len(self.variables)
        if self.signal_hub:
            self.signal_hub.emit("varmanager_initialized", {
                "variable_count": variable_count,
                "node_count": len(nodes)
            })

    def get_input(self, node: dict) -> List[Any]:
        """
        Get input values for a node.
        
        Args:
            node: Node dictionary
            
        Returns:
            List of input values
            
        Raises:
            ValueError: If legacy input format is used
        """
        input_vars = node.get("input", [])
        values = []

        for inp in input_vars:
            if isinstance(inp, dict):
                if "var" in inp:
                    var_name = inp["var"]
                    val = self.variables.get(var_name)
                    values.append(val)
                elif "value" in inp:
                    # Make sure literals are numbers
                    values.append(inp["value"])
            else:
                raise ValueError(f"Legacy input format not supported: {inp}")

        return values

    def set_output(self, node_id: str, output_values: Any) -> None:
        """
        Set output values for a node.
        
        Args:
            node_id: Node ID
            output_values: Output value(s) - can be single value or list/tuple
            
        Raises:
            ValueError: If output count doesn't match expected count
        """
        outputs = self.node_output_map.get(node_id, [])
        if not outputs:
            return  # No outputs

        if not isinstance(output_values, (list, tuple)):
            output_values = [output_values]

        if len(outputs) != len(output_values):
            raise ValueError(f"Output mismatch for node {node_id}: expected {len(outputs)} got {len(output_values)}")

        for var_name, val in zip(outputs, output_values):
            old_value = self.variables.get(var_name)
            self.variables[var_name] = val
            
            # Emit variable_set signal if value changed (optional, can be verbose)
            if self.signal_hub and old_value != val:
                self.signal_hub.emit("variable_set", {
                    "var_name": var_name,
                    "old_value": old_value,
                    "new_value": val,
                    "node_id": node_id
                })