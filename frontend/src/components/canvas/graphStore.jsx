let currentGraph = null;

export function setGraph(graph) {
  currentGraph = structuredClone(graph);
}

export function getGraph() {
  return structuredClone(currentGraph);
}

// Optimistic updates
export function updateNodePosition(nodeId, position) {
  if (!currentGraph) return;

  const node = currentGraph.nodes.find(n => n.nodeId === nodeId);
  if (!node) return;

  node.ui = node.ui || {};
  node.ui.position = position;
}

export function updateGraphFromBackend(graph) {
  // Backend always wins
  setGraph(graph);
}
