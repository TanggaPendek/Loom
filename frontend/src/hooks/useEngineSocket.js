import { useState, useEffect, useRef, useCallback } from "react";

const WS_URL = "ws://localhost:8000/ws/engine";
const RECONNECT_DELAY_MS = 2000;

/**
 * useEngineSocket
 * Connects to the Loom backend WebSocket and tracks engine state.
 * Returns: { engineStatus: "idle"|"running", lastMessage: string }
 */
export function useEngineSocket() {
  const [engineStatus, setEngineStatus] = useState("idle");
  const [lastMessage, setLastMessage] = useState("Connecting…");
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;
        setLastMessage("Connected to Loom engine");
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "engine_status") {
            setEngineStatus(msg.status);
            if (msg.message) setLastMessage(msg.message);
          }
          // ignore ping frames
        } catch {
          // ignore malformed frames
        }
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        setLastMessage("Disconnected — reconnecting…");
        reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY_MS);
      };

      ws.onerror = () => {
        ws.close(); // triggers onclose → reconnect
      };
    } catch {
      reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY_MS);
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { engineStatus, lastMessage };
}
