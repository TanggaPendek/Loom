import React, { useState, useEffect, useRef } from 'react';
import { Download, FileText, Loader2 } from 'lucide-react';
import { getEngineLogs } from '../../api/commands';

const LogsPanel = ({ isPolling }) => {
    const [logs, setLogs] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const logsEndRef = useRef(null);
    const pollingInterval = useRef(null);

    // Auto-scroll to bottom when new logs appear
    const scrollToBottom = () => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [logs]);

    // Poll logs from backend
    const fetchLogs = async () => {
        try {
            setIsLoading(true);
            const response = await getEngineLogs();

            if (response.status === 'ok' && response.logs) {
                setLogs(response.logs);
            }
        } catch (error) {
            console.error('Failed to fetch logs:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Start/stop polling based on engine state
    useEffect(() => {
        if (isPolling) {
            // Clear logs on new run
            setLogs([]);

            // Initial fetch
            fetchLogs();

            // Start polling every 2 seconds
            pollingInterval.current = setInterval(fetchLogs, 2000);
        } else {
            // Stop polling when engine idle
            if (pollingInterval.current) {
                clearInterval(pollingInterval.current);
                pollingInterval.current = null;
            }
        }

        // Cleanup on unmount
        return () => {
            if (pollingInterval.current) {
                clearInterval(pollingInterval.current);
            }
        };
    }, [isPolling]);

    // Export logs as JSON
    const handleExport = () => {
        const dataStr = JSON.stringify(logs, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `loom-logs-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="h-full flex flex-col p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <FileText size={18} className="text-emerald-600" />
                    <h3 className="font-black text-sm uppercase tracking-tight text-emerald-900">
                        Execution Logs
                    </h3>
                    {isPolling && (
                        <Loader2 size={14} className="text-emerald-500 animate-spin" />
                    )}
                </div>

                {logs.length > 0 && (
                    <button
                        onClick={handleExport}
                        className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-600 rounded-lg text-xs font-semibold transition-all"
                        title="Export logs as JSON"
                    >
                        <Download size={14} />
                        Export
                    </button>
                )}
            </div>

            {/* Logs Container - Matching emerald theme */}
            <div className="flex-1 bg-emerald-50/30 border-2 border-emerald-100/50 rounded-[22px] p-4 overflow-y-auto">
                {logs.length === 0 ? (
                    <div className="flex items-center justify-center h-full">
                        {isPolling ? (
                            <div className="flex flex-col items-center gap-3">
                                <Loader2 size={20} className="text-emerald-500 animate-spin" />
                                <span className="text-sm text-emerald-600/60 font-medium">Waiting for logs...</span>
                            </div>
                        ) : (
                            <span className="text-sm text-emerald-600/40 font-medium">No logs. Run the engine to see output.</span>
                        )}
                    </div>
                ) : (
                    <>
                        {logs.map((log, index) => {
                            // Handle both old format (timestamp/message) and new format (time/msg)
                            const timeStr = log.time || log.timestamp;
                            const message = log.msg || log.message;

                            return (
                                <div
                                    key={index}
                                    className="group mb-2 p-3 bg-white/60 hover:bg-white rounded-[16px] border border-emerald-100/30 hover:border-emerald-200 transition-all"
                                >
                                    <div className="flex items-start gap-3">
                                        {timeStr && (
                                            <span className="text-[10px] font-mono text-emerald-500/50 font-semibold mt-0.5 flex-shrink-0">
                                                {new Date(timeStr).toLocaleTimeString()}
                                            </span>
                                        )}
                                        <span className="text-xs text-emerald-900 leading-relaxed flex-1">
                                            {message}
                                        </span>
                                    </div>
                                </div>
                            );
                        })}
                        <div ref={logsEndRef} />
                    </>
                )}
            </div>

            {/* Footer Info */}
            <div className="mt-3 text-center">
                {logs.length > 0 && (
                    <span className="text-[10px] text-emerald-600/40 font-bold uppercase tracking-widest">
                        {logs.length} {logs.length === 1 ? 'Entry' : 'Entries'}
                    </span>
                )}
            </div>
        </div>
    );
};

export default LogsPanel;
