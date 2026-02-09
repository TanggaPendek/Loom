import { useState, useCallback, useEffect, useRef } from "react";
import ReactFlow, {
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  Controls,
  Background,
  MarkerType,
} from "reactflow";
import "reactflow/dist/style.css";
import { useReactFlow } from "reactflow";
import DynamicNode from "./dynamicNode";
import LoomEdge from "../universal/loomEdge";
import { loadGraph as loadGraphAPI } from "../../api/commands";
import { loadGraph } from "./graphLoader";
import CottonEdge from "./cottonEdge";
import {
  deleteGraphNode,
  moveGraphNode,
  addGraphNode,
  editGraphNode,
  createConnection,
  deleteConnection,
  updateGraphNodeInput,
} from "../../api/commands";

const NODE_TYPES = { dynamicNode: DynamicNode };
const EDGE_TYPES = { loom: LoomEdge };

export default function Canvas({
  onRegisterRefresh,
  onSelect,
  onNodesUpdate,
  onEdgesUpdate,
}) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);

  const edgeTypes = {
    cotton: CottonEdge,
  };

  // Notify parent when edges change
  useEffect(() => {
    if (onEdgesUpdate) {
      onEdgesUpdate(edges);
    }
  }, [edges, onEdgesUpdate]);

  // --- 1. SELECTION HANDLERS ---
  const onNodeClick = useCallback(
    (_, node) => {
      if (node.dragging) return;
      onSelect({ ...node, type: "node" });
    },
    [onSelect],
  );

  const onEdgeClick = useCallback(
    (_, edge) => {
      onSelect({ ...edge, type: "edge" });
    },
    [onSelect],
  );

  const onPaneClick = useCallback(() => {
    onSelect(null);
  }, [onSelect]);

  // --- 2. INPUT HANDLER (Fixed Scope) ---
  const onInputChange = useCallback((nodeId, index, val) => {
    // 1. Update UI immediately
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          const nextInputs = [...(node.data.inputs || [])];
          nextInputs[index] = { ...nextInputs[index], value: val };
          return { ...node, data: { ...node.data, inputs: nextInputs } };
        }
        return node;
      }),
    );

    // 2. Sync with backend (debounced fire-and-forget)
    updateGraphNodeInput(nodeId, index, val).catch((err) => {
      console.error(`Failed to update input value:`, err);
    });
  }, []);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onNodeDragStop = useCallback(
    (event, node) => {
      console.log(
        `LOOM: Node ${node.id} moved to (${node.position.x}, ${node.position.y})`,
      );

      // Update backend with new position
      moveGraphNode(node.id, node.position.x, node.position.y).catch((err) => {
        console.error(`Failed to update node position:`, err);
      });

      // Notify parent component
      onNodesUpdate?.(nodes);
    },
    [nodes, onNodesUpdate],
  );
  const onDrop = useCallback(
    async (event) => {
      event.preventDefault();
      if (!reactFlowInstance) return;

      const rawData = event.dataTransfer.getData("application/reactflow");
      if (!rawData) return;
      const droppedData = JSON.parse(rawData);

      // Calculate position with a slight offset to center the node
      const bounds = event.currentTarget.getBoundingClientRect();
      const position = reactFlowInstance.project({
        x: event.clientX - bounds.left - 50,
        y: event.clientY - bounds.top - 20,
      });

      /* --- API SECTION --- */
      const response = await addGraphNode(
        droppedData.label,
        position.x,
        position.y,
      );

      // CRITICAL: The dispatcher returns handler data inside 'result'
      if (response?.status === "ok" && response.node) {
        const backendNode = response.node;

        const newNode = {
          id: backendNode.nodeId,
          type: "dynamicNode",
          position: backendNode.position,
          data: {
            label: backendNode.name,
            // Map inputs to handle both {var: ...} and {value: ...}
            inputs: backendNode.input.map((inp, idx) => ({
              var: inp.var,
              value: "",
            })),
            // Map outputs as strings from the list
            outputs: backendNode.output.map((out) => ({
              id: out,
              label: out,
            })),
            onChange: (key, value) =>
              onInputChange(backendNode.nodeId, key, value),
          },
        };

        setNodes((nds) => nds.concat(newNode));
      } else {
        console.error(
          "LOOM Error: Check backend handler for 'node_create_request'",
        );
      }
    },
    [reactFlowInstance, setNodes, onInputChange],
  );

  const onNodesChange = useCallback(
    (chs) => setNodes((nds) => applyNodeChanges(chs, nds)),
    [],
  );
  // Remove the current onEdgesChange and onEdgesDelete
  // Replace with this combined handler:

  const onEdgesChange = useCallback(
    (changes) => {
      // Intercept remove changes to sync with backend BEFORE updating UI
      const removeChanges = changes.filter((c) => c.type === "remove");

      if (removeChanges.length > 0) {
        removeChanges.forEach((change) => {
          const edge = edges.find((e) => e.id === change.id);
          if (!edge) return;

          console.log(`LOOM: Cutting thread ${edge.id}`);

          // Resolve the ports from the edge handles
          const sourcePort = resolvePortIndex(
            edge.source,
            edge.sourceHandle,
            "source",
          );
          const targetPort = resolvePortIndex(
            edge.target,
            edge.targetHandle,
            "target",
          );

          // Validate ports exist
          if (sourcePort < 0 || targetPort < 0) {
            console.error(
              "LOOM Error: Invalid port mapping for edge deletion",
              {
                edge,
                sourcePort,
                targetPort,
              },
            );
            return;
          }

          // Send full payload to backend (fire-and-forget)
          deleteConnection(
            edge.source,
            sourcePort,
            edge.target,
            targetPort,
          ).catch((err) => {
            console.error(`Failed to sever connection ${edge.id}:`, err);
          });
        });
      }

      // Apply all changes to UI (including the removes)
      setEdges((eds) => applyEdgeChanges(changes, eds));
    },
    [edges, nodes], // Add nodes dependency for resolvePortIndex
  );

  // REMOVE the old onEdgesDelete callback entirely
  // DELETE THIS:
  // const onEdgesDelete = useCallback((deletedEdges) => { ... }, []);
  const onNodesDelete = useCallback(async (deletedNodes) => {
    for (const node of deletedNodes) {
      try {
        console.log(`LOOM: Severing node ${node.id}`);
        await deleteGraphNode(node.id);
      } catch (error) {
        console.error("Failed to delete node:", error);
      }
    }
  }, []);

  // --- 3. REFRESH LOGIC ---
  const refreshGraph = useCallback(async () => {
    setLoading(true);
    setIsAnimating(true);

    // 1. Start the animation timer (at least one full turn)
    const animationTimer = new Promise((resolve) => setTimeout(resolve, 600));

    try {
      // 2. Fetch the "truth" instantly
      const res = await loadGraphAPI();

      if (res?.graph) {
        const { nodes: initialNodes, edges: initialEdges } = loadGraph(
          res.graph,
          onInputChange, // Pass the callback
        );
        setNodes(initialNodes.map((n) => ({ ...n, type: "dynamicNode" })));
        setEdges(
          initialEdges.map((e) => ({ ...e, type: "cotton", animated: false })),
        );
      }

      // 3. Wait for the animation to finish its rotation even if data is already here
      await animationTimer;
      return res;
    } finally {
      setLoading(false);
      setIsAnimating(false);
    }
  }, [onInputChange]);

  // --- 4. LIFECYCLE ---
  useEffect(() => {
    onRegisterRefresh(refreshGraph);
    refreshGraph();
  }, [onRegisterRefresh, refreshGraph]);

  // In Canvas.jsx
  useEffect(() => {
    if (onRegisterRefresh) {
      onRegisterRefresh(() => refreshGraph);
    }
    refreshGraph();
  }, [onRegisterRefresh, refreshGraph]);
  useEffect(() => {
    onNodesUpdate?.(nodes);
  }, [nodes]);

  const resolvePortIndex = (nodeId, handleId, type) => {
    const node = nodes.find((n) => n.id === nodeId);
    if (!node) {
      console.error(`Node not found: ${nodeId}`);
      return -1;
    }

    if (type === "source") {
      // outputs is an array like [{id: "Value", label: "Value"}, ...] or ["Value", ...]
      const index = node.data.outputs.findIndex(
        (o) => (typeof o === "string" ? o : o.id) === handleId,
      );
      if (index < 0) {
        console.error(
          `Output handle not found: ${handleId} in node ${nodeId}`,
          node.data.outputs,
        );
      }
      return index;
    }

    if (type === "target") {
      // inputs is an array like [{var: "inputs", value: ""}, ...]
      const index = node.data.inputs.findIndex(
        (i) => (i.var ?? "") === handleId,
      );
      if (index < 0) {
        console.error(
          `Input handle not found: ${handleId} in node ${nodeId}`,
          node.data.inputs,
        );
      }
      return index;
    }

    return -1;
  };

  // --- 6. EDGE HANDLERS (Optimistic Weaving) ---

  const onConnect = useCallback(
    (params) => {
      // 1. Optimistic UI update
      const tempId = `edge-${Date.now()}`;
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            id: tempId,
            type: "cotton",
            animated: false,
          },
          eds,
        ),
      );

      // 2. Resolve handle IDs → port indices
      const sourcePort = resolvePortIndex(
        params.source,
        params.sourceHandle,
        "source",
      );
      const targetPort = resolvePortIndex(
        params.target,
        params.targetHandle,
        "target",
      );

      // 3. Validation
      if (sourcePort < 0 || targetPort < 0) {
        console.error("LOOM Error: Invalid port mapping", {
          source: params.source,
          sourceHandle: params.sourceHandle,
          sourcePort,
          target: params.target,
          targetHandle: params.targetHandle,
          targetPort,
        });
        // Optionally: Remove the optimistic edge
        setEdges((eds) => eds.filter((e) => e.id !== tempId));
        return;
      }

      // 4. Send to backend with correct signature
      createConnection(
        params.source, // sourceNodeId
        sourcePort, // sourcePort (integer)
        params.target, // targetNodeId
        targetPort, // targetPort (integer)
      ).catch((err) => {
        console.error("Backend failed to create connection:", err);
        // Remove optimistic edge on failure
        setEdges((eds) => eds.filter((e) => e.id !== tempId));
      });
    },
    [nodes], // Add setEdges to dependencies if needed
  );

  const onEdgesDelete = useCallback(
    (deletedEdges) => {
      deletedEdges.forEach((edge) => {
        console.log(`LOOM: Cutting thread ${edge.id}`);

        // Resolve the ports from the edge handles
        const sourcePort = resolvePortIndex(
          edge.source,
          edge.sourceHandle,
          "source",
        );
        const targetPort = resolvePortIndex(
          edge.target,
          edge.targetHandle,
          "target",
        );

        // Validate ports exist
        if (sourcePort < 0 || targetPort < 0) {
          console.error("LOOM Error: Invalid port mapping for edge deletion", {
            edge,
            sourcePort,
            targetPort,
          });
          return;
        }

        // Send full payload to backend
        deleteConnection(
          edge.source, // sourceNodeId
          sourcePort, // sourcePort (integer)
          edge.target, // targetNodeId
          targetPort, // targetPort (integer)
        ).catch((err) => {
          console.error(`Failed to sever connection ${edge.id}:`, err);
        });
      });
    },
    [nodes],
  );

  // --- 5. RENDER ---
  return (
    <div className="w-full h-full bg-[#FCFDFB] relative overflow-hidden">
      {/* Texture Overlay */}
      <div
        className="absolute inset-0 pointer-events-none opacity-40 z-0"
        style={{ filter: "url(#canvas-cotton-texture)" }}
      />

      {/* Floating UI: Refresh Button */}
      <div className="absolute top-8 right-8 z-50">
        <button
          onClick={refreshGraph}
          disabled={loading || isAnimating}
          className="group w-12 h-12 flex items-center justify-center rounded-full bg-white 
                     shadow-[0_4px_20px_rgba(16,185,129,0.15)] hover:shadow-[0_4px_20px_rgba(244,63,94,0.2)]
                     text-emerald-500 hover:text-rose-500 transition-all duration-300 active:scale-90"
        >
          <svg
            className={`w-6 h-6 transition-all duration-700 ease-in-out ${
              isAnimating ? "animate-spin text-rose-500" : ""
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="3"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </button>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={NODE_TYPES}
        edgeTypes={edgeTypes}
        defaultEdgeOptions={{
          type: "cotton",
          animated: false,
        }}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
        onPaneClick={onPaneClick}
        onInit={setReactFlowInstance} // CRITICAL: Captures the instance for coordinate projection
        onDrop={onDrop} // Handle the drop
        onDragOver={onDragOver} // Allow the drop
        onNodesDelete={onNodesDelete}
        onConnect={onConnect}
        onEdgesDelete={onEdgesDelete}
        onNodeDragStop={onNodeDragStop}
        fitView
        className="relative z-10"
      >
        <Background variant="dots" color="#10b981" gap={32} opacity={0.15} />
        <Controls
          showInteractive={false}
          className="!bg-white !border-2 !border-emerald-50 !rounded-[20px] !m-8 !shadow-lg"
        />
      </ReactFlow>
    </div>
  );
}
