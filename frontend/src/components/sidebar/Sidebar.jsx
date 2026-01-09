// src/components/sidebar/Sidebar.jsx
import React from 'react';
import { useNodeLibrary } from './script/useNodeLibrary';
import Node from '../universal/node/node'; 

export default function Sidebar() {
  // Destructure the values from your hook
  const { nodes, loading, refresh } = useNodeLibrary();

  const handleManualClick = () => {
    console.log("1. UI: Button Clicked");
    if (typeof refresh === 'function') {
      console.log("2. UI: Calling refresh function from hook...");
      refresh();
    } else {
      console.error("2. UI ERROR: refresh is not a function!", refresh);
    }
  };

  return (
    <div className="w-64 h-full bg-gray-50 border-r flex flex-col font-sans">
      <div className="p-3 border-b flex justify-between items-center bg-white">
        <span className="font-bold text-xs text-gray-500 uppercase">Node Bank</span>
        
        <button 
          onClick={handleManualClick} // Use our logged handler
          disabled={loading}
          className="p-1.5 rounded-md hover:bg-gray-100"
        >
          <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {nodes.map((node, i) => (
          <Node key={node.nodeId || i} data={node} context="sidebar" />
        ))}
      </div>
    </div>
  );
}