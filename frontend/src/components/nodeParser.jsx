let nodeIdCounter = 1;

export function parseNode(def, position = { x: 0, y: 0 }) {
  const id = `n${nodeIdCounter++}`;

  const node = {
    id,
    type: "dynamicNode",
    position,
    data: {
      label: def.label || def.type || "Node",
      inputs: Array.isArray(def.dynamic?.inputs) ? def.dynamic.inputs : [],
      outputs: Array.isArray(def.dynamic?.outputs) ? def.dynamic.outputs : [],
      controls: Array.isArray(def.dynamic?.controls) ? def.dynamic.controls : [],
      onChange: () => {},
    },
  };

  return node;
}
