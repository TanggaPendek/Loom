import React from "react";
import { Handle, Position } from "reactflow";

export default function NodeDynamic({ data, showHandles }) {
  const { inputs, outputs, controls, onChange } = data.dynamic || {};

  return (
    <div className="relative flex flex-col items-center">
      {/* Target Handles (Left) */}
      {showHandles && inputs?.map((id, i) => (
        <Handle key={id} type="target" position={Position.Left} id={id} 
                style={{ top: 30 + i * 20 }} className="bg-blue-500" />
      ))}

      {/* Controls (Inputs/Textboxes) */}
      <div className="w-full space-y-2">
        {controls?.map((ctrl) => (
          <div key={ctrl.key} className="flex flex-col">
            <label className="text-[10px] text-gray-500">{ctrl.label}</label>
            <input 
              type="text" 
              className="nodrag text-[10px] p-1 border rounded bg-white/50"
              onChange={(e) => onChange?.(ctrl.key, e.target.value)}
            />
          </div>
        ))}
      </div>

      {/* Source Handles (Right) */}
      {showHandles && outputs?.map((id, i) => (
        <Handle key={id} type="source" position={Position.Right} id={id} 
                style={{ top: 30 + i * 20 }} className="bg-green-500" />
      ))}
    </div>
  );
}