import { useState, useCallback, useEffect } from "react";
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

const NODE_TYPES = { dynamicNode: DynamicNode };
const EDGE_TYPES = { loom: LoomEdge };

export default function Canvas({ onRegisterRefresh, onSelect, onNodesUpdate }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  const edgeTypes = {
    cotton: CottonEdge,
  };

  // --- 1. SELECTION HANDLERS ---
  // Change this in your Canvas component
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
  }, []);

  const onNodesChange = useCallback(
    (chs) => setNodes((nds) => applyNodeChanges(chs, nds)),
    [],
  );
  const onEdgesChange = useCallback(
    (chs) => setEdges((eds) => applyEdgeChanges(chs, eds)),
    [],
  );

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
  }, []);

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

  const onConnect = useCallback(
    (params) => {
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            type: "cotton",
            animated: false, // <- lock it
          },
          eds,
        ),
      );
    },
    [setEdges],
  );

  // --- 5. RENDER ---
  return (
    <div className="w-full h-full bg-[#FCFDFB] relative overflow-hidden">
      {/* SVG Cotton Texture Filter */}
      <svg className="hidden">
        <filter id="canvas-cotton-texture">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.8"
            numOctaves="3"
            stitchTiles="stitch"
          />
          <feColorMatrix
            type="matrix"
            values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.05 0"
          />
          <feComposite operator="in" in2="SourceGraphic" />
        </filter>
      </svg>

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
        onConnect={onConnect}
        fitView
        className="relative z-10"
        onNodeDragStop={(_, node) => {
          moveNode(node.id, node.position.x, node.position.y);
        }}
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
