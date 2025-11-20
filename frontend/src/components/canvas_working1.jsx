// src/components/Canvas.jsx
import { useState, useCallback } from "react";
import {
  ReactFlow,
  applyEdgeChanges,
  applyNodeChanges,
  addEdge,
  Controls,
  Background,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

export default function Canvas() {
  const initialNodes = [
    {
      id: "n1",
      position: { x: 0, y: 0 },
      data: { label: "Node 1" },
      type: "input",
    },
  ];
  const initialEdges = [];

  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  const onNodesChange = useCallback(
    (changes) =>
      setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot)),
    []
  );
  const onEdgesChange = useCallback(
    (changes) =>
      setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)),
    []
  );
  const onConnect = useCallback(
    (params) => setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
    []
  );

  // Drop handler
  const onDrop = useCallback(
    (event) => {
      event.preventDefault();
      const reactFlowBounds = event.currentTarget.getBoundingClientRect();
      const data = JSON.parse(event.dataTransfer.getData("application/reactflow"));

      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      };

      const newNode = {
        id: `n${nodes.length + 1}`,
        type: data.type || "default",
        position,
        data: { label: data.label },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [nodes]
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  return (
    <div style={{ height: "100%", width: "100%" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
