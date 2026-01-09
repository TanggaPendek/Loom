// src/api/client.js
const BASE_URL = "http://127.0.0.1:8000";

export const get = async (endpoint) => {
  console.log("API CALLING:", endpoint); // If this doesn't show in console, the button is broken
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`);
    if (!response.ok) throw new Error("Network response was not ok");
    return await response.json();
  } catch (error) {
    console.error("FETCH ERROR:", error);
    return null;
  }
};

export const request = async (cmd, payload = {}) => {
  const response = await fetch(`${BASE_URL}/dispatch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cmd, ...payload }),
  });
  return response.json();
};