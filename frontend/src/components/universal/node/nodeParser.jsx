let nodeIdCounter = 1;

/**
 * Converts a Node Bank definition into a React Flow node object.
 * @param {Object} definition - The JSON from nodeindex.json
 * @param {Object} position - {x, y} coordinates on the canvas
 * @returns {Object} - A React Flow compatible node
 */
export const parseNodeForCanvas = (definition, position = { x: 0, y: 0 }) => {
  // 1. Generate a unique ID for the canvas instance
  const id = `node_${Date.now()}_${nodeIdCounter++}`;

  // 2. Build the React Flow node structure
  return {
    id,
    type: "universalNode", // This must match your 'nodeTypes' mapping in the Canvas
    position,
    // The 'data' object is what gets passed to your UniversalNode component
    data: {
      ...definition, // Spread name, type, metadata from JSON
      label: definition.name || "New Node",
      // Ensure dynamic properties exist so the UI doesn't crash
      dynamic: {
        inputs: definition.dynamic?.inputs || [],
        outputs: definition.dynamic?.outputs || [],
        controls: definition.dynamic?.controls || [],
      },
      // Add a placeholder for change events
      onChange: (key, value) => {
        console.log(`Node ${id} changed: ${key} = ${value}`);
      }
    },
  };
};