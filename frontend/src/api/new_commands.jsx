// New API commands for engine state and logs
import { request } from "./client";

// Engine state and logs
export const getEngineState = () => request("engine_get_state");
export const getEngineLogs = (projectId) => request("engine_get_logs", { project_id: projectId });

// Custom nodes
export const listCustomNodes = () => request("custom_node_list");
export const getCustomNode = (name) => request("custom_node_get", { name });
export const createCustomNode = (name, code, metadata) => request("custom_node_create", { name, code, metadata });
export const updateCustomNode = (name, code) => request("custom_node_update", { name, code });
export const deleteCustomNode = (name) => request("custom_node_delete", { name });
export const validateCustomNode = (code) => request("custom_node_validate", { code });
