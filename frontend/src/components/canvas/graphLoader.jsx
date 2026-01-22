export const loadGraph = (graphData) => {
  // 1. Map Nodes
  const nodes = graphData.nodes.map((n) => ({
    id: n.nodeId,
    type: "dynamicNode",
    position: n.position,
    data: {
      label: n.name,
      inputs: n.input || [],
      outputs: n.output || [],
    },
  }));

  // 2. Map Connections to Edges
  const edges = (graphData.connections || []).map((c) => ({
    id: c.connectionId,
    source: c.sourceNodeId,
    target: c.targetNodeId,
    // CRITICAL: These must match the Handle IDs in DynamicNode.jsx
    sourceHandle: c.sourceOutput, // e.g., "out_1"
    targetHandle: c.targetInput,  // e.g., "var_1"
    type: "loom",
    animated: true,
  }));

  return { nodes, edges };
};