import { request } from './client';


// --- ENGINE ---
export const runEngine = () => request("run");
export const stopEngine = () => request("stop");
export const forceStop = () => request("force_stop");

// --- PROJECT ---
export const initProject = () => request("init");
export const createProject = (name) => request("create", { name });
export const deleteProject = (id) => request("delete", { id });

// --- NODES ---
export const addNode = (type, x, y) => request("node_add", { type, x, y });
export const moveNode = (id, x, y) => request("node_move", { id, x, y });
export const deleteNode = (id) => request("node_delete", { id });
export const fetchNodeIndex = () => request("init_nodes");

// src/api/commands.js
import { get } from './client';

export const getStartupData = async () => {
  console.log("3. API: commands.js calling client.get('/startup')");
  return await get("/startup");
};