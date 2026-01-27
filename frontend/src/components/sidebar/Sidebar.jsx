import React from "react";
import { useState, useCallback, useEffect } from "react";
import { useNodeLibrary } from "./script/useNodeLibrary";
import Node from "../universal/node/node";

export default function Sidebar() {
  const { nodes, loading, refresh } = useNodeLibrary();
  const [isSpinning, setIsSpinning] = useState(false);



const onDragStart = (event, nodeData) => {
    // We package the backend node data to be parsed by the Canvas
    const dragData = {
      label: nodeData.name,
      inputs: nodeData.input || [],
      outputs: nodeData.output || [],
      controls: nodeData.controls || [],
    };
    
    event.dataTransfer.setData("application/reactflow", JSON.stringify(dragData));
    event.dataTransfer.effectAllowed = "move";
  };

  const handleManualClick = async (e) => {
    e.stopPropagation();
    if (typeof refresh !== "function" || isSpinning) return;
    setIsSpinning(true);
    const spinTimer = new Promise((resolve) => setTimeout(resolve, 600));
    try {
      await Promise.all([refresh(), spinTimer]);
    } finally {
      setIsSpinning(false);
    }
  };

  return (
    <>
      {/* SVG Cotton Texture Filter Definition */}
      <svg className="hidden">
        <filter id="cotton-texture">
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

      {/* Main Container: Squircle 32px, Creamy Cotton Foundation */}
      <div
        className="w-72 h-full bg-[#FCFDFB] border-r border-emerald-100 flex flex-col relative overflow-hidden"
        style={{ borderRadius: "0 32px 32px 0" }} // External Squircle logic
      >
        {/* Cotton Texture Overlay */}
        <div
          className="absolute inset-0 pointer-events-none opacity-50"
          style={{ filter: "url(#cotton-texture)" }}
        />

        {/* Header Section */}
        <div className="p-8 flex justify-between items-center relative z-10">
          <span className="font-bold text-[10px] text-emerald-700 uppercase tracking-[0.2em]">
            Node Bank
          </span>

          {/* High-Contrast Refresh/Action Button */}
          <button
            onClick={handleManualClick}
            disabled={loading || isSpinning}
            className="group w-11 h-11 flex items-center justify-center rounded-full bg-white 
                       shadow-[0_4px_20px_rgba(16,185,129,0.15)] hover:shadow-[0_4px_20px_rgba(244,63,94,0.2)]
                       text-emerald-500 hover:text-rose-500 transition-all duration-300 active:scale-95"
          >
            <svg
              className={`w-5 h-5 transition-all duration-700 ease-in-out ${
                isSpinning || loading ? "animate-spin text-rose-500" : ""
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

        {/* Scrolling Area: Internal Squircle 24px for Node cards */}
        <div className="flex-1 overflow-y-auto px-6 pb-8 space-y-6 relative z-10">
          {nodes.map((node, i) => (
            <div
              key={node.nodeId || i}
              draggable // 1. Enable dragging
              onDragStart={(e) => onDragStart(e, node)} // 2. Attach handler
              className="bg-white rounded-[24px] shadow-sm shadow-emerald-50 border border-emerald-50/50 
                         hover:shadow-md hover:shadow-emerald-100 transition-all duration-300 
                         active:scale-[0.98] cursor-grab active:cursor-grabbing"
            >
              <Node data={node} context="sidebar" />
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
