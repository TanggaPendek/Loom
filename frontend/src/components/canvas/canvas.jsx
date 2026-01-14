import { useState, useCallback, useEffect } from "react";
import ReactFlow, {
  applyNodeChanges,
  applyEdgeChanges,
  Controls,
  Background,
} from "reactflow";
import "reactflow/dist/style.css";

import DynamicNode from "./dynamicNode";
import { loadGraph as loadGraphAPI } from "../../api/commands";
import { loadGraph } from "./graphLoader";
export default function Canvas({ onRegisterRefresh }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const nodeTypes = { dynamicNode: DynamicNode }; // 👈 ADD THIS

  const refreshGraph = async () => {
    const res = await loadGraphAPI();
    if (!res?.graph) return;

    const { nodes, edges } = loadGraph(res.graph);
    setNodes(nodes);
    setEdges(edges);
  };

  useEffect(() => {
    onRegisterRefresh(() => refreshGraph);
    refreshGraph(); 
  }, []);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <div style={{ padding: 4 }}>
        <button onClick={refreshGraph}>🔄 Refresh Graph</button>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
