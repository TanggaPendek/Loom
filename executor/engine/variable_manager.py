# variable_manager.py
class VariableManager:
    def __init__(self):
        self.variables = {}  # variable_name -> value
        self.node_output_map = {}  # nodeId -> list of output variable names

    def init_variables(self, nodes):
        """
        Initialize variables for all nodes.
        Primitive inputs are pre-set if provided in metadata (applied to outputs if needed).
        """
        for node in nodes:
            node_id = node["nodeId"]

            # initialize outputs
            outputs = node.get("output", [])
            self.node_output_map[node_id] = outputs

            metadata = node.get("metadata", {})
            defaults = metadata.get("defaults", {})

            for out_var in outputs:
                # assign default if exists, else None
                self.variables[out_var] = defaults.get(out_var, None)

            # initialize primitive inputs if defaults exist for input names
            # only for literal default values, skip actual input descriptors
            for inp in node.get("input", []):
                if isinstance(inp, dict) and "var" not in inp and "value" in inp:
                    # one-off literal default for this node, stored in a temp var name if needed
                    # optional: skip, since literals don’t need global storage
                    pass


    def get_input(self, node):
        input_vars = node.get("input", [])
        values = []

        for inp in input_vars:
            if isinstance(inp, dict):
                if "var" in inp:
                    var_name = inp["var"]
                    val = self.variables.get(var_name)
                    values.append(val)
                elif "value" in inp:
                    # make sure literals are numbers
                    values.append(inp["value"])
            else:
                raise ValueError(f"Legacy input format not supported: {inp}")

        return values




    def set_output(self, node_id, output_values):
        outputs = self.node_output_map.get(node_id, [])
        if not outputs:
            return  # no outputs

        if not isinstance(output_values, (list, tuple)):
            output_values = [output_values]

        if len(outputs) != len(output_values):
            raise ValueError(f"Output mismatch for node {node_id}: expected {len(outputs)} got {len(output_values)}")

        for var_name, val in zip(outputs, output_values):
            self.variables[var_name] = val

