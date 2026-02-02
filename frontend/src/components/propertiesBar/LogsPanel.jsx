import React, { useState, useEffect } from 'react';
import { Trash2, FileText } from 'lucide-react';

/**
 * LogsPanel Component
 * Displays execution logs when no element is selected
 */
const LogsPanel = ({ logs, isPolling }) => {
    const scrollRef = React.useRef(null);

    // Auto-scroll to bottom when new logs arrive
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="flex flex-col h-full">
            <div className="flex items-center justify-between p-4 border-b border-emerald-100/50 bg-emerald-50/30">
                <div className="flex items-center gap-2">
                    <FileText size={16} className="text-emerald-600" />
                    <h3 className="font-black text-xs uppercase tracking-wider text-emerald-900">
                        Execution Logs
                    </h3>
                </div>
                {isPolling && (
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                        <span className="text-[9px] text-emerald-600 font-mono">Live</span>
                    </div>
                )}
            </div>

            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-4 space-y-2 bg-gradient-to-b from-white to-emerald-50/20"
            >
                {logs.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-emerald-300">
                        <FileText size={32} className="mb-2 opacity-50" />
                        <p className="text-xs font-mono">No logs yet</p>
                        <p className="text-[10px] opacity-70 mt-1">Run the engine to see output</p>
                    </div>
                ) : (
                    logs.map((log, index) => (
                        <div
                            key={index}
                            className={`p-3 rounded-xl border transition-all ${log.level === 'error'
                                    ? 'bg-rose-50 border-rose-200'
                                    : log.level === 'warning'
                                        ? 'bg-amber-50 border-amber-200'
                                        : 'bg-white border-emerald-100'
                                }`}
                        >
                            <div className="flex items-start justify-between gap-2 mb-1">
                                <span className={`text-[8px] font-black uppercase tracking-widest ${log.level === 'error'
                                        ? 'text-rose-600'
                                        : log.level === 'warning'
                                            ? 'text-amber-600'
                                            : 'text-emerald-600'
                                    }`}>
                                    {log.nodeId}
                                </span>
                                <span className="text-[8px] text-gray-400 font-mono">
                                    {new Date(log.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                            <p className="text-xs font-mono text-gray-700 leading-relaxed">
                                {log.message}
                            </p>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default LogsPanel;
