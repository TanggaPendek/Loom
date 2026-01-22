import React, { useState, useEffect } from 'react';
import { Play, Square, Settings, Zap, Database, AlertCircle } from 'lucide-react';
// Import your API functions
import { runEngine, stopEngine, forceStop, updateNodeData } from '../../api/commands'; 

const PropertiesBar = ({ selectedElement, onUpdateValue }) => {
  const [engineState, setEngineState] = useState('idle');
  const [localInputs, setLocalInputs] = useState([]);

  useEffect(() => {
    if (selectedElement?.data?.inputs) {
      setLocalInputs(selectedElement.data.inputs);
    } else {
      setLocalInputs([]);
    }
  }, [selectedElement?.id]);

  const isNode = selectedElement?.type === 'node';
  const data = selectedElement?.data || {};

  // LOCAL UI UPDATE (FAST)
  const handleTyping = (idx, newValue) => {
    const updated = [...localInputs];
    updated[idx] = { ...updated[idx], value: newValue };
    setLocalInputs(updated);
  };

  // 1. TYPE 1 API: AUTO-COMMIT ON BLUR
  const handleBlurCommit = async (idx, finalValue) => {
    // Sync the visual canvas state first
    onUpdateValue(idx, finalValue);

    // Call your 'request' based API
    console.log("📡 Dispatching node_update...");
    const response = await updateNodeData(selectedElement.id, {
      index: idx,
      value: finalValue,
      // Pass the full data object if your backend expects the whole state:
      // full_inputs: localInputs 
    });

    if (!response) {
      console.error("Failed to sync to backend");
      // Optional: Handle retry or visual error state here
    }
  };

  // 2. TYPE 2 API: ENGINE COMMANDS
  const handleEngineAction = async (actionType) => {
    let res;
    if (actionType === 'START') {
      setEngineState('running');
      res = await runEngine();
    } else if (actionType === 'STOP') {
      setEngineState('idle');
      res = await stopEngine();
    } else if (actionType === 'FORCE') {
      setEngineState('idle');
      res = await forceStop();
    }
    
    if (!res) {
      console.error(`Engine ${actionType} command failed`);
      setEngineState('idle');
    }
  };

  return (
    <div className="h-full flex flex-col bg-white/80 backdrop-blur-2xl">
      {/* HEADER */}
      <header className="p-6 border-b border-emerald-100/50 bg-emerald-50/30">
        {selectedElement ? (
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-emerald-600 rounded-[18px] flex items-center justify-center text-white shadow-lg shadow-emerald-200 ring-4 ring-emerald-50">
              {isNode ? <Zap size={20} fill="currentColor" /> : <Database size={20} />}
            </div>
            <div>
              <h2 className="font-black text-sm uppercase tracking-tight text-emerald-900 leading-none mb-1">
                {isNode ? data.label : "Edge Link"}
              </h2>
              <span className="text-[9px] font-mono text-emerald-600/50 bg-emerald-100/50 px-1.5 py-0.5 rounded">
                ID: {selectedElement.id}
              </span>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-4 opacity-50">
            <div className="w-12 h-12 bg-slate-200 rounded-[18px] flex items-center justify-center text-slate-400">
              <Settings size={20} />
            </div>
            <h2 className="font-black text-sm uppercase tracking-tight text-slate-400">System Standby</h2>
          </div>
        )}
      </header>

      {/* BODY - Inputs with onBlur trigger */}
      <div className="flex-1 overflow-y-auto p-6">
        {selectedElement && isNode && localInputs && (
          <div className="space-y-4">
            {localInputs.map((inp, idx) => (
              <div key={idx} className="group p-4 bg-white border-2 border-emerald-50 rounded-[22px] hover:border-emerald-200 transition-all shadow-sm">
                <label className="block text-[9px] font-black text-emerald-800/40 uppercase tracking-widest mb-2">
                  {inp.var ? `Ref: ${inp.var}` : `Literal Value`}
                </label>
                {"value" in inp ? (
                  <input
                    type="text"
                    className="w-full bg-emerald-50/50 border-none rounded-xl px-3 py-2 text-xs font-mono text-emerald-700 outline-none"
                    value={inp.value}
                    onChange={(e) => handleTyping(idx, e.target.value)}
                    onBlur={(e) => handleBlurCommit(idx, e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && e.target.blur()}
                  />
                ) : (
                  <div className="px-3 py-2 bg-emerald-900/5 rounded-xl text-xs font-mono text-emerald-900/40 italic">Linked</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* FOOTER - Engine Controls */}
      <footer className="p-6 border-t border-emerald-100/50 bg-emerald-50/40">
        <div className="flex flex-col gap-3">
          {engineState === 'idle' ? (
            <button 
              onClick={() => handleEngineAction('START')}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white py-4 rounded-[24px] font-black text-[11px] uppercase tracking-[0.2em] flex items-center justify-center gap-3"
            >
              <Play size={16} fill="white" /> Run Loom
            </button>
          ) : (
            <>
              <button 
                onClick={() => handleEngineAction('STOP')}
                className="w-full bg-rose-500 hover:bg-rose-600 text-white py-4 rounded-[24px] font-black text-[11px] uppercase tracking-[0.2em] flex items-center justify-center gap-3"
              >
                <Square size={16} fill="white" /> Stop Engine
              </button>
              <button 
                onClick={() => handleEngineAction('FORCE')}
                className="w-full flex items-center justify-center gap-2 py-2 text-rose-400 hover:text-rose-600 text-[9px] font-black uppercase tracking-widest"
              >
                <AlertCircle size={12} /> Force Kill
              </button>
            </>
          )}
        </div>
      </footer>
    </div>
  );
};

export default PropertiesBar;