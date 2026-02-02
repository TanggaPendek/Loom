import React, { useMemo, memo } from "react";
import { Handle, Position, useEdges } from "reactflow";

const DynamicNode = ({ id, data, selected }) => {
  const edges = useEdges();

  // 1. Guard Clause
  if (!data) {
    return (
      <div className="w-10 h-10 border-4 border-emerald-100 border-t-emerald-500 rounded-full animate-spin" />
    );
  }

  const { label = "Node", inputs = [], outputs = [], onChangeValue } = data;

  // 2. Connection Tracking Logic (from Code 1)
  const connectedHandles = useMemo(() => {
    const targets = new Set();
    const sources = new Set();

    edges.forEach((edge) => {
      if (edge.target === id) targets.add(edge.targetHandle);
      if (edge.source === id) sources.add(edge.sourceHandle);
    });

    return { targets, sources };
  }, [edges, id]);

  return (
    <div
      className={`bg-[#FCFDFB] border-2 rounded-[24px] shadow-xl transition-all duration-300
        ${selected
          ? "border-emerald-500 ring-4 ring-emerald-500/10 scale-[1.02]"
          : "border-emerald-100 shadow-emerald-100/20"
        } active:scale-[0.98]`}
    >
      {/* Header */}
      <div className="bg-emerald-500 px-5 py-3 text-white font-black text-[10px] uppercase tracking-[0.2em] rounded-t-[22px]">
        {label}
      </div>

      <div className="p-5 space-y-6 relative">
        {/* SVG Texture Overlay */}
        <div
          className="absolute inset-0 pointer-events-none opacity-[0.04]"
          style={{ filter: "url(#cotton-texture)" }}
        />

        {/* INPUTS SECTION */}

        <div className="space-y-4 relative z-10">
          {inputs.map((inp, i) => {
            // Use the actual variable name as the handle ID
            const handleId = inp.var || `var_${i + 1}`;
            const isConnected = connectedHandles.targets.has(handleId);

            return (
              <div key={handleId} className="relative flex flex-col gap-1">
                <Handle
                  type="target"
                  position={Position.Left}
                  id={handleId}
                  className={`!w-4 !h-4 !border-[3px] !-left-[30px] transition-all duration-300 shadow-sm ${isConnected
                    ? "!bg-emerald-500 !border-emerald-200 scale-110"
                    : "!bg-white !border-emerald-500"
                    }`}
                />

                <label className="text-[9px] font-black text-emerald-800 uppercase tracking-widest ml-1">
                  {inp.var ? inp.var : "Literal Value"}
                </label>

                <input
                  type="text"
                  className={`nodrag w-full px-3 py-2 border-2 rounded-[12px] text-xs font-mono transition-all ${isConnected
                    ? "bg-emerald-50/50 border-emerald-200 text-emerald-900"
                    : "bg-white border-emerald-50 text-emerald-400 italic"
                    } focus:outline-none focus:border-emerald-400`}
                  defaultValue={inp.value}
                  onBlur={(e) => {
                    if (!isConnected) {
                      e.stopPropagation();
                      onChangeValue?.(i, e.target.value);
                    }
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !isConnected) {
                      e.stopPropagation();
                      e.target.blur(); // Trigger onBlur
                    }
                  }}
                  disabled={isConnected} // disable input if linked
                  placeholder={isConnected ? "Linked..." : "Enter value..."}
                />
              </div>
            );
          })}
        </div>

        {/* OUTPUTS SECTION */}
        {outputs.length > 0 && (
          <div className="pt-4 border-t border-emerald-50 space-y-3 relative z-10">
            {outputs.map((out, i) => {
              const outLabel =
                typeof out === "string" ? out : out.label || `Out ${i + 1}`;
              const handleId =
                typeof out === "string" ? out : out.id || `out_${i + 1}`;
              const isConnected = connectedHandles.sources.has(handleId);

              return (
                <div
                  key={handleId}
                  className="relative flex items-center justify-end"
                >
                  <span
                    className={`text-[10px] font-black uppercase tracking-widest mr-2 transition-colors ${isConnected ? "text-rose-600" : "text-emerald-200"
                      }`}
                  >
                    {outLabel}
                  </span>
                  <Handle
                    type="source"
                    position={Position.Right}
                    id={handleId}
                    className={`!w-4 !h-4 !border-[3px] !-right-[30px] transition-all duration-300 shadow-sm ${isConnected
                      ? "!bg-rose-500 !border-rose-200 scale-110"
                      : "!bg-white !border-rose-500"
                      }`}
                  />
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default memo(DynamicNode);
