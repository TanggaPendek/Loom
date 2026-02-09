import React, { useState, useEffect } from "react";
import {
  Play,
  Square,
  Settings,
  Zap,
  Database,
  AlertCircle,
  Trash2,
} from "lucide-react";
import LogsPanel from "./LogsPanel";
import { get } from "../../api/client";
import {
  runEngine,
  stopEngine,
  forceStop,
  updateGraphNodeInput,
  deleteGraphNode,
  deleteConnection,
} from "../../api/commands";

const PropertiesBar = ({ selectedElement, onUpdateValue, edges }) => {
  const [engineState, setEngineState] = useState("idle"); // 'idle' or 'running'
  const [localInputs, setLocalInputs] = useState([]);
  const [logs, setLogs] = useState([]);
  const [lastLogTimestamp, setLastLogTimestamp] = useState(null);

  // Poll logs only when engine is running
  useEffect(() => {
    if (engineState !== "running") return;

    const pollLogs = async () => {
      try {
        const url = lastLogTimestamp
          ? `/sync/logs?since=${lastLogTimestamp}`
          : "/sync/logs";

        const response = await get(url);

        if (response?.logs && response.logs.length > 0) {
          setLogs((prev) => [...prev, ...response.logs]);
          // Update timestamp to the latest log
          const latest = response.logs[response.logs.length - 1];
          setLastLogTimestamp(latest.timestamp);
        }
      } catch (error) {
        console.error("Failed to fetch logs:", error);
      }
    };

    const interval = setInterval(pollLogs, 2000);
    return () => clearInterval(interval);
  }, [engineState, lastLogTimestamp]);

  // Clear logs when engine starts
  useEffect(() => {
    if (engineState === "running") {
      setLogs([]);
      setLastLogTimestamp(null);
    }
  }, [engineState]);

  // Update local inputs when selection changes
  useEffect(() => {
    if (selectedElement?.data?.inputs) {
      setLocalInputs(selectedElement.data.inputs);
    } else {
      setLocalInputs([]);
    }
  }, [selectedElement?.id]);

  const isNode = selectedElement?.type === "node";
  const isEdge = selectedElement?.type === "edge";
  const data = selectedElement?.data || {};

  // Check if input has connection
  const hasConnection = (inputIndex) => {
    if (!edges || !selectedElement) return false;

    const input = localInputs[inputIndex];
    if (!input) return false;

    return edges.some(
      (edge) =>
        edge.target === selectedElement.id && edge.targetHandle === input.var,
    );
  };

  // LOCAL UI UPDATE (FAST)
  const handleTyping = (idx, newValue) => {
    const updated = [...localInputs];
    updated[idx] = { ...updated[idx], value: newValue };
    setLocalInputs(updated);
  };

  // AUTO-COMMIT ON BLUR
  const commitValue = async (idx, finalValue) => {
    // Sync with canvas
    if (onUpdateValue) {
      onUpdateValue(idx, finalValue);
    }

    // Sync with backend
    try {
      await updateGraphNodeInput(selectedElement.id, idx, finalValue);
      console.log(
        `PropertiesBar: Committed value for input ${idx}:`,
        finalValue,
      );
    } catch (error) {
      console.error("Failed to update node input:", error);
    }
  };

  // DELETE HANDLER
  const handleDelete = async () => {
    if (!selectedElement) return;

    const confirmDelete = window.confirm(
      `Are you sure you want to delete this ${isNode ? "node" : "edge"}?`,
    );

    if (!confirmDelete) return;

    try {
      if (isNode) {
        await deleteGraphNode(selectedElement.id);
      } else if (isEdge) {
        // For edges, we need to extract the connection details
        const edge = selectedElement;
        // Resolve port indices from handles
        const sourceNode = edges.find((e) => e.id === edge.id);
        if (sourceNode) {
          await deleteConnection(
            edge.source,
            edge.sourceHandle,
            edge.target,
            edge.targetHandle,
          );
        }
      }

      // Trigger canvas refresh (parent component handles this)
      console.log("Element deleted successfully");
    } catch (error) {
      console.error("Failed to delete element:", error);
    }
  };

  // SIMPLIFIED ENGINE COMMANDS - await response for state management
  const handleEngineAction = async (actionType) => {
    try {
      if (actionType === "START") {
        setEngineState("running"); // Set to running immediately
        await runEngine(); // Wait for completion
        setEngineState("idle"); // Return to idle when done
      } else if (actionType === "STOP") {
        await stopEngine();
        setEngineState("idle");
      } else if (actionType === "FORCE") {
        await forceStop();
        setEngineState("idle");
      }
    } catch (error) {
      console.error(`Engine ${actionType} command failed:`, error);
      setEngineState("idle"); // Reset to idle on error
    }
  };

  return (
    <div className="h-full flex flex-col bg-white/80 backdrop-blur-2xl">
      {/* HEADER */}
      <header className="p-6 border-b border-emerald-100/50 bg-emerald-50/30">
        {selectedElement ? (
          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-emerald-600 rounded-[18px] flex items-center justify-center text-white shadow-lg shadow-emerald-200 ring-4 ring-emerald-50">
                {isNode ? (
                  <Zap size={20} fill="currentColor" />
                ) : (
                  <Database size={20} />
                )}
              </div>
              <div className="flex-1">
                <h2 className="font-black text-sm uppercase tracking-tight text-emerald-900 leading-none mb-1">
                  {isNode ? data.label : "Connection"}
                </h2>
                <span className="text-[9px] font-mono text-emerald-600/50 bg-emerald-100/50 px-1.5 py-0.5 rounded">
                  ID: {selectedElement.id}
                </span>
              </div>
            </div>

            {/* DELETE BUTTON */}
            <button
              onClick={handleDelete}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-rose-50 hover:bg-rose-100 text-rose-600 hover:text-rose-700 rounded-[16px] transition-all border-2 border-rose-200 hover:border-rose-300 font-black text-[10px] uppercase tracking-wider"
            >
              <Trash2 size={14} />
              Delete {isNode ? "Node" : "Connection"}
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-4 opacity-70">
            <div className="w-12 h-12 bg-slate-200 rounded-[18px] flex items-center justify-center text-slate-400">
              <Settings size={20} />
            </div>
            <h2 className="font-black text-sm uppercase tracking-tight text-slate-400">
              Properties
            </h2>
          </div>
        )}
      </header>

      {/* BODY */}
      <div className="flex-1 overflow-y-auto">
        {selectedElement && isNode ? (
          <div className="p-6 space-y-4">
            {localInputs.map((inp, idx) => {
              const connected = hasConnection(idx);

              return (
                <div
                  key={idx}
                  className="group p-4 bg-white border-2 border-emerald-50 rounded-[22px] hover:border-emerald-200 transition-all shadow-sm"
                >
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-[9px] font-black text-emerald-800/40 uppercase tracking-widest">
                      {inp.var || "Value"}
                    </label>
                    {connected && (
                      <span className="text-[8px] font-mono bg-emerald-100 text-emerald-600 px-2 py-0.5 rounded">
                        Connected
                      </span>
                    )}
                  </div>

                  <input
                    type="text"
                    className={`w-full px-3 py-2 border-none rounded-xl text-xs font-mono outline-none transition-all ${
                      connected
                        ? "bg-emerald-50/30 text-emerald-400 cursor-not-allowed"
                        : "bg-emerald-50/50 text-emerald-700"
                    }`}
                    value={inp.value || ""}
                    onChange={(e) => handleTyping(idx, e.target.value)}
                    onBlur={(e) => {
                      if (!connected) {
                        commitValue(idx, e.target.value);
                      }
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !connected) {
                        commitValue(idx, e.target.value);
                        e.target.blur();
                      }
                    }}
                    disabled={connected}
                    placeholder={
                      connected ? "Using connection..." : "Enter value..."
                    }
                  />

                  {connected && (
                    <p className="text-[9px] text-emerald-500 mt-1 italic">
                      Value ignored during execution
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        ) : selectedElement && isEdge ? (
          <div className="p-6">
            <div className="p-4 bg-emerald-50 rounded-[22px] border-2 border-emerald-100">
              <p className="text-xs text-emerald-700">
                <span className="font-black">Source:</span>{" "}
                {selectedElement.source}
              </p>
              <p className="text-xs text-emerald-700 mt-2">
                <span className="font-black">Target:</span>{" "}
                {selectedElement.target}
              </p>
            </div>
          </div>
        ) : (
          <LogsPanel logs={logs} isPolling={engineState === "running"} />
        )}
      </div>

      {/* FOOTER - Engine Controls */}
      <footer className="p-6 border-t border-emerald-100/50 bg-emerald-50/40">
        <div className="flex flex-col gap-3">
          {engineState === "idle" ? (
            <button
              onClick={() => handleEngineAction("START")}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white py-4 rounded-[24px] font-black text-[11px] uppercase tracking-[0.2em] flex items-center justify-center gap-3 transition-all active:scale-95"
            >
              <Play size={16} fill="white" /> Run Loom
            </button>
          ) : (
            <>
              <button
                onClick={() => handleEngineAction("STOP")}
                className="w-full bg-rose-500 hover:bg-rose-600 text-white py-4 rounded-[24px] font-black text-[11px] uppercase tracking-[0.2em] flex items-center justify-center gap-3 transition-all active:scale-95"
              >
                <Square size={16} fill="white" /> Stop Engine
              </button>
              <button
                onClick={() => handleEngineAction("FORCE")}
                className="w-full flex items-center justify-center gap-2 py-2 text-rose-400 hover:text-rose-600 text-[9px] font-black uppercase tracking-widest transition-colors"
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
