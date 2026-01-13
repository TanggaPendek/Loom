const BASE_URL = "http://127.0.0.1:8000";

export const get = async (endpoint) => {
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`);
    if (!res.ok) throw new Error(res.statusText);
    return await res.json();
  } catch (err) {
    console.error("GET ERROR:", endpoint, err);
    return null;
  }
};

export const request = async (cmd, payload = {}) => {
  try {
    const res = await fetch(`${BASE_URL}/dispatch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd, ...payload }),
    });
    if (!res.ok) throw new Error(res.statusText);
    return await res.json();
  } catch (err) {
    console.error("DISPATCH ERROR:", cmd, err);
    return null;
  }
};