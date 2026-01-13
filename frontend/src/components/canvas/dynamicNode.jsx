import { Handle, Position } from "reactflow";
import "./dynamicNode.css";

export default function DynamicNode({ data }) {
  const {
    label,
    inputs = [],
    outputs = [],
    metadata = {},
  } = data;

  return (
    <div className="dyn-node">
      {/* Header */}
      <div className="dyn-node-header">
        {label}
      </div>

      {/* Metadata / operation */}
      {metadata?.operation && (
        <div className="dyn-node-meta">
          op: {metadata.operation}
        </div>
      )}
      {metadata?.type && (
        <div className="dyn-node-meta">
          type: {metadata.type}
        </div>
      )}

      {/* Inputs */}
      <div className="dyn-node-section">
        {inputs.map((inp, i) => (
          <div className="dyn-node-row" key={`in-${i}`}>
            <Handle
              type="target"
              position={Position.Left}
              id={`var_${i + 1}`}
            />
            <span className="dyn-node-text">
              {"var" in inp ? `var: ${inp.var}` : `value: ${inp.value}`}
            </span>
          </div>
        ))}
      </div>

      {/* Outputs */}
      <div className="dyn-node-section">
        {outputs.map((out, i) => (
          <div className="dyn-node-row right" key={`out-${i}`}>
            <span className="dyn-node-text">{out}</span>
            <Handle
              type="source"
              position={Position.Right}
              id={out}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
