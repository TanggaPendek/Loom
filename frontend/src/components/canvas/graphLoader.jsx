
export function loadGraph(graph) {
  if (!graph) return { nodes: [], edges: [] };

  const nodes = graph.nodes.map((n) => ({
    id: n.nodeId,
    type: "dynamicNode",
    position: n.position || { x: 0, y: 0 },
    data: {
      label: n.name,
      inputs: n.input || [],
      outputs: n.output || [],
      metadata: {
        ...n.metadata,
        ref: n.ref,
        positionId: n.positionId,
      },
    },
  }));

  const edges = graph.connections.map((c) => ({
    id: c.connectionId,
    source: c.sourceNodeId,
    target: c.targetNodeId,
    sourceHandle: c.sourceOutput,
    targetHandle: c.targetInput,
    label: c.metadata?.label || "",
  }));

  return { nodes, edges };
}
