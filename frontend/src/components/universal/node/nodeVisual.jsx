import React, { useMemo } from 'react';
import NodeDynamic from './nodeDynamic';

export default function NodeVisual({ data, showHandles, isMini }) {
  // Memoize color so it doesn't change every re-render
  const bgColor = useMemo(() => {
    const hue = Math.floor(Math.random() * 360);
    return `hsl(${hue}, 70%, 85%)`;
  }, []);

  return (
    <div 
      className={`rounded-xl border border-gray-300 shadow-md transition-all
        ${isMini ? 'p-2 w-full text-xs' : 'p-4 min-w-[150px] bg-white'} 
        ${!isMini && 'hover:shadow-xl hover:border-indigo-400'}`}
      style={{ backgroundColor: bgColor, color: "#1e293b" }}
    >
      <div className={`font-bold mb-2 ${isMini ? 'text-[10px]' : 'text-sm'}`}>
        {data.name || data.label}
      </div>

      {/* Only show full dynamic guts if it's NOT a mini sidebar version */}
      {!isMini && <NodeDynamic data={data} showHandles={showHandles} />}
      
      {isMini && (
        <div className="text-[9px] opacity-60 italic">
          {data.metadata?.description || "Custom Node"}
        </div>
      )}
    </div>
  );
}