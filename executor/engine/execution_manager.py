# execution_manager.py
import asyncio
from collections import deque

class ExecutionManager:
    def __init__(self, nodes, loaded_nodes, variable_manager, connections):
        """
        nodes: list of node dicts from JSON
        loaded_nodes: node_id -> function
        variable_manager: VariableManager instance
        connections: list of connection dicts from JSON
        """
        self.nodes = {node["nodeId"]: node for node in nodes}  # map node_id -> node dict
        self.loaded_nodes = loaded_nodes
        self.var_mgr = variable_manager
        self.connections = connections

        # build dependency graph
        self.dependencies = self._build_dependencies()

    def _build_dependencies(self):
        # node_id -> set of node_ids it depends on
        dep_map = {node_id: set() for node_id in self.nodes}
        # build var -> producing node map from VariableManager
        var_to_node = {}
        for conn in self.connections:
            var_to_node[conn["sourceOutput"]] = conn["sourceNodeId"]

        for node_id, node in self.nodes.items():
            for inp in node.get("input", []):
                if isinstance(inp, dict) and "var" in inp:
                    producer = var_to_node.get(inp["var"])
                    if producer:
                        dep_map[node_id].add(producer)
        return dep_map

    def _topological_sort(self):
        in_degree = {node: len(deps) for node, deps in self.dependencies.items()}
        ready = deque([n for n, deg in in_degree.items() if deg == 0])
        order = []

        while ready:
            node = ready.popleft()
            order.append(node)
            for n, deps in self.dependencies.items():
                if node in deps:
                    deps.remove(node)
                    in_degree[n] -= 1
                    if in_degree[n] == 0:
                        ready.append(n)

        if len(order) != len(self.dependencies):
            raise ValueError("Graph has cycles!")
        return order

    def run_linear(self):
        """Run nodes sequentially based on topological sort"""
        execution_order = self._topological_sort()
        for node_id in execution_order:
            node = self.nodes[node_id]
            func = self.loaded_nodes[node_id]
            inputs = self.var_mgr.get_input(node)
            output = func(inputs, self.var_mgr.variables)
            self.var_mgr.set_output(node_id, output)
            print(f"[ExecutionManager] Node {node_id} executed, output={output}")

    async def run_node_async(self, node_id):
        node = self.nodes[node_id]
        func = self.loaded_nodes[node_id]
        inputs = self.var_mgr.get_input(node)
        output = func(inputs, self.var_mgr.variables)
        self.var_mgr.set_output(node_id, output)
        print(f"[ExecutionManager] Node {node_id} executed (async), output={output}")

    async def run_parallel(self):
        """Run nodes in topological order, but independent nodes concurrently"""
        execution_order = self._topological_sort()
        # naive approach: run each node as a task sequentially
        # later, you can improve by batching independent nodes
        tasks = [self.run_node_async(node_id) for node_id in execution_order]
        await asyncio.gather(*tasks)
