import React from "react";
import { Handle, Position } from "reactflow";

export default function DynamicNode({ data }) {
  const { label, inputs, outputs, controls, onChange } = data;

  return (
    <div
      className="relative flex flex-col items-center p-4 rounded-2xl border border-gray-300
                 bg-gradient-to-br from-indigo-50 via-white to-pink-50 shadow-lg hover:shadow-2xl
                 transition-all duration-300 font-sans min-w-[140px]"
    >
      {/* Inputs */}
      {inputs?.map((id, i) => (
        <Handle
          key={id || i}
          type="target"
          id={id}
          position={Position.Left}
          style={{
            top: 28 + i * 22,
            width: 12,
            height: 12,
            borderRadius: "50%",
            border: "2px solid white",
            transition: "all 0.2s",
          }}
          className="bg-blue-500 hover:bg-blue-600"
        />
      ))}

      {/* Label */}
      <div className="text-center font-bold text-sm md:text-base text-gray-900 mb-3 drop-shadow-sm">
        {label}
      </div>

      {/* Controls */}
      {controls?.map((control) => {
        if (control.type === "text") {
          return (
            <div key={control.key} className="w-full mb-3 flex flex-col">
              <label className="text-[10px] text-gray-600 mb-1 tracking-wide">
                {control.label}
              </label>
              <input
                type="text"
                value={data[control.key] || ""}
                onChange={(e) => onChange?.(control.key, e.target.value)}
                className="nodrag w-full px-2 py-1 rounded-lg border border-gray-300 
                           text-xs focus:outline-none focus:ring-2 focus:ring-purple-400 
                           placeholder-gray-400 transition-all duration-200"
                placeholder={`Enter ${control.label.toLowerCase()}`}
              />
            </div>
          );
        }
        return null;
      })}

      {/* Outputs */}
      {outputs?.map((id, i) => (
        <Handle
          key={id || i}
          type="source"
          id={id}
          position={Position.Right}
          style={{
            top: 28 + i * 22,
            width: 12,
            height: 12,
            borderRadius: "50%",
            border: "2px solid white",
            transition: "all 0.2s",
          }}
          className="bg-green-400 hover:bg-green-500"
        />
      ))}
    </div>
  );
}
