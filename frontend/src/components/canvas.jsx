import React, { useState, useCallback } from "react";
import ReactFlow, { addEdge, Controls, Background } from "reactflow";
import "reactflow/dist/style.css";

export default function Canvas() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => nds.map((node) => {
      const change = changes.find(c => c.id === node.id);
      return change ? { ...node, ...change } : node;
    })),
    []
  );

  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => eds.map((edge) => {
      const change = changes.find(c => c.id === edge.id);
      return change ? { ...edge, ...change } : edge;
    })),
    []
  );

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  const onPaneDrop = useCallback((event) => {
    event.preventDefault();

    // Get the node info from the palette
    const reactFlowData = event.dataTransfer.getData("application/reactflow");
    if (!reactFlowData) return;

    const nodeData = JSON.parse(reactFlowData);

    // Calculate drop position relative to canvas
    const reactFlowBounds = event.currentTarget.getBoundingClientRect();
    const position = {
      x: event.clientX - reactFlowBounds.left,
      y: event.clientY - reactFlowBounds.top
    };

    // Add node using the format React Flow expects
    setNodes((nds) => [
      ...nds,
      {
        id: `${Date.now()}`,
        type: nodeData.type || "default",
        position,
        data: { label: nodeData.label },
      },
    ]);
  }, []);

  const onPaneDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  return (
    <ReactFlow
      className="w-full h-full"
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      onPaneDrop={onPaneDrop}
      onPaneDragOver={onPaneDragOver}
      fitView
    >
      <Controls />
      <Background color="#aaa" gap={16} />
    </ReactFlow>
  );
}
