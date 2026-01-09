import { useState, useEffect, useCallback } from 'react';
import { getStartupData } from '../../../api/commands';

export const useNodeLibrary = () => {
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    console.log("⚡ Refreshing Node Library..."); // DEBUG 1
    setLoading(true);
    try {
      const data = await getStartupData();
      console.log("📦 Backend Data:", data); // DEBUG 2
      
      if (data && data.node_index) {
        setNodes(data.node_index);
      }
    } catch (err) {
      console.error(" API Request Failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load when component mounts
  useEffect(() => {
    refresh();
  }, [refresh]);

  return { nodes, loading, refresh };
};