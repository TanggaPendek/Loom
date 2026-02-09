import { request, get } from "./client";

/* ---------- ENGINE (Actions) ---------- */
export const runEngine = () => request("run");
export const stopEngine = () => request("stop");
export const forceStop = () => request("force_stop");

/* ---------- DATA FETCHING (Sync) ---------- */
// These now use the 'get' helper and the dynamic /sync/ path
export const getStartupData = () => get("/sync/startup");
export const loadGraph = () => get("/sync/load_graph");

/* ---------- PROJECT (Actions) ---------- */
export const initProject = () => request("init");
export const createProject = (data) => request("project_create", data);
export const deleteProject = (projectId) => request("project_delete", { projectId });
export const loadProject = (projectId) => request("project_load", { projectId });
export const selectProject = (projectId) => request("project_load", { projectId });
export const openProject = (projectId) => request("project_open", { projectId });

/* ---------- NODES (Actions) ---------- */
export const addNode = (type, x, y) =>
  request("node_add", { type, x, y });

export const moveNode = (id, x, y) =>
  request("node_move", { id, x, y });

export const deleteNode = (id) =>
  request("node_delete", { id });

// If this is fetching a list, use get, if it's triggering a rebuild, use request
export const fetchNodeIndex = () => get("/sync/node_index");


/* ---------- GRAPH NODES (Project Graph) ---------- */
export const addGraphNode = (type, x, y) =>
  request("graph_node_add", { type, x, y });

export const editGraphNode = (nodeId, updates) =>
  request("graph_node_edit", { nodeId, updates });

export const deleteGraphNode = (nodeId) =>
  request("graph_node_delete", { nodeId });

export const moveGraphNode = (nodeId, x, y) =>
  request("graph_node_edit", { nodeId, updates: { position: { x, y } } });

export const updateGraphNodeInput = (nodeId, inputIndex, value) =>
  request("graph_node_update_input", {
    nodeId,
    inputIndex,
    value
  });


/* ---------- CONNECTIONS (Actions) ---------- */
export const createConnection = (sourceNodeId, sourcePort, targetNodeId, targetPort) => {
  return request("connection_create", {
    sourceNodeId,
    sourcePort,    // Backend expects integer index (0, 1, 2...)
    targetNodeId,
    targetPort     // Backend expects integer index (0, 1, 2...)
  });
};

export const deleteConnection = (sourceNodeId, sourcePort, targetNodeId, targetPort) => {
  return request("connection_delete", {
    sourceNodeId,
    sourcePort,
    targetNodeId,
    targetPort
  });
};


// Legacy alias for backward compatibility (do not break old imports)
export const updateNodeData = (nodeId, updates) => editGraphNode(nodeId, updates);

/* ---------- ENGINE STATE & LOGS ---------- */
export const getEngineState = () => request("engine_get_state");
export const getEngineLogs = (projectId) => request("engine_get_logs", { project_id: projectId });

/* ---------- CUSTOM NODES ---------- */
export const listCustomNodes = () => request("custom_node_list");
export const getCustomNode = (name) => request("custom_node_get", { name });
export const createCustomNode = (name, code, metadata) => request("custom_node_create", { name, code, metadata });
export const updateCustomNode = (name, code) => request("custom_node_update", { name, code });
export const deleteCustomNode = (name) => request("custom_node_delete", { name });
export const validateCustomNode = (code) => request("custom_node_validate", { code });
