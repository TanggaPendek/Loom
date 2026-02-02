export const loadGraph = (graphData) => {
  // 1. Map Nodes first
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

  // 2. Helper function to get handle ID from port index
  const getHandleId = (nodeId, portIndex, isSource) => {
    const node = graphData.nodes.find((n) => n.nodeId === nodeId);
    if (!node) return null;

    if (isSource) {
      // For outputs: use the output string itself as handle ID
      const outputs = node.output || [];
      return outputs[portIndex] || null;
    } else {
      // For inputs: use the "var" property as handle ID
      const inputs = node.input || [];
      const input = inputs[portIndex];
      return input?.var || null;
    }
  };

  // 3. Map Connections to Edges with correct handle IDs
  const edges = (graphData.connections || []).map((c, index) => {
    const sourceHandle = getHandleId(c.sourceNodeId, c.sourcePort, true);
    const targetHandle = getHandleId(c.targetNodeId, c.targetPort, false);

    return {
      id: `edge-${c.sourceNodeId}-${c.sourcePort}-${c.targetNodeId}-${c.targetPort}`,
      source: c.sourceNodeId,
      target: c.targetNodeId,
      sourceHandle: sourceHandle,
      targetHandle: targetHandle,
      type: "cotton",
      animated: false,
    };
  });

  return { nodes, edges };
};