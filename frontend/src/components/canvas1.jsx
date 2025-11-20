import { useState, useCallback } from "react";
import ReactFlow, {
  applyEdgeChanges,
  applyNodeChanges,
  addEdge,
  Controls,
  Background,
} from "reactflow";
import "reactflow/dist/style.css";

import DynamicNode from "./dynamicNode";
import { parseNode } from "./nodeParser";

export default function Canvas() {
  const initialNodes = [
    {
      id: "n1",
      type: "dynamicNode",
      position: { x: 0, y: 0 },
      data: {
        label: "Start Node",
        inputs: [],
        outputs: [],
        controls: [],
        onChange: () => {},
      },
    },
  ];

  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);

  const nodeTypes = { dynamicNode: DynamicNode };

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );
  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  

  // Update control values in node data
  const handleControlChange = useCallback((nodeId, key, value) => {
    setNodes((nds) =>
      nds.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, [key]: value } } : n
      )
    );
  }, []);

const onDrop = useCallback(
  (event) => {
    event.preventDefault();
    if (!reactFlowInstance) return;

    const data = JSON.parse(event.dataTransfer.getData("application/reactflow"));
    const bounds = event.currentTarget.getBoundingClientRect();
    const position = reactFlowInstance.project({
      x: event.clientX - bounds.left - 50,
      y: event.clientY - bounds.top - 20,
    });

    // Parse node
    const dynamicNode = parseNode(data, position);

    // Add onChange referencing the node ID
    dynamicNode.data.onChange = (key, value) => {
      setNodes((nds) =>
        nds.map((n) =>
          n.id === dynamicNode.id
            ? { ...n, data: { ...n.data, [key]: value } }
            : n
        )
      );
    };

    setNodes((nds) => nds.concat(dynamicNode));
  },
  [reactFlowInstance]
);


  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        fitView
        onInit={setReactFlowInstance}
        nodeTypes={nodeTypes}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
