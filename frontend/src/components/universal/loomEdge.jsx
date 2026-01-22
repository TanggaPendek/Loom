import React from 'react';
import { Handle, Position } from "reactflow";

export default function DynamicNode({ data }) {
  // 1. THE GUARD: If data isn't ready, show a loading squircle or return null
  if (!data) {
    return (
      <div className="w-10 h-10 border-4 border-emerald-100 border-t-emerald-500 rounded-full animate-spin" />
    );
  }

  // 2. SAFE DESTRUCTURING
  const { label = "New Node", inputs = [], outputs = [], onChangeValue } = data;

  const handleInputChange = (e, index) => {
    e.stopPropagation();
    if (onChangeValue) {
      onChangeValue(index, e.target.value);
    }
  };

  return (
    <div className="bg-[#FCFDFB] border-2 border-emerald-100 rounded-[24px] shadow-xl shadow-emerald-100/20 overflow-hidden min-w-[220px] active:scale-[0.99] transition-transform">
      {/* High-Contrast Header */}
      <div className="bg-emerald-500 px-5 py-3 text-white font-black text-[10px] uppercase tracking-[0.2em]">
        {label}
      </div>

      <div className="p-5 space-y-4 relative">
        <div className="absolute inset-0 pointer-events-none opacity-[0.04]" style={{ filter: 'url(#cotton-texture)' }} />

        {/* Interactive Inputs */}
        <div className="space-y-4 relative z-10">
          {inputs.map((inp, i) => (
            <div className="relative flex flex-col gap-1" key={`in-${i}`}>
              <Handle
                type="target"
                position={Position.Left}
                id={`var_${i + 1}`}
                className="!w-4 !h-4 !bg-white !border-[3px] !border-emerald-500 !-left-[30px] shadow-md shadow-emerald-200/50"
              />
              
              <label className="text-[9px] font-black text-emerald-800 uppercase tracking-widest ml-1">
                {inp.var ? `Variable: ${inp.var}` : `Constant Value`}
              </label>

              <input
                type="text"
                className="nodrag w-full px-3 py-2 bg-white border-2 border-emerald-50 rounded-[12px] 
                           text-xs font-mono text-emerald-900 focus:outline-none focus:border-emerald-400 
                           focus:shadow-[0_0_0_4px_rgba(16,185,129,0.1)] transition-all"
                defaultValue={inp.value}
                onChange={(e) => handleInputChange(e, i)}
                onKeyDown={(e) => e.stopPropagation()}
                placeholder="Enter value..."
              />
            </div>
          ))}
        </div>

        {/* Outputs - Rose Contrast */}
        <div className="space-y-3 relative z-10 pt-2">
           {outputs.map((out, i) => (
            <div className="relative flex items-center justify-end" key={`out-${i}`}>
              <span className="text-[10px] text-rose-600 font-black uppercase tracking-widest mr-2">{out}</span>
              <Handle
                type="source"
                position={Position.Right}
                id={out}
                className="!w-4 !h-4 !bg-white !border-[3px] !border-rose-500 !-right-[30px] shadow-md shadow-rose-200/50"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}