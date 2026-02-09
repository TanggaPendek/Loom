// src/components/Sidebar.jsx
import React from 'react';
import NodeItem from './nodeItem';

// Define example nodes with dynamic structure
const nodeDefinitions = [
  {
    label: 'Int',
    type: 'custom',
    dynamic: {
      outputs: ['value'], // single output
      controls: [
        {
          type: 'text',
          key: 'value',    // this key will hold the input value
          label: 'Value',  // label displayed above textbox
        },
      ],
    },
    data: {
      label: 'Int',
      dynamic: {
        outputs: ['value'],
        controls: [
          {
            type: 'text',
            key: 'value',
            label: 'Value',
          },
        ],
      },
    },
  },
  {
    label: 'Add',
    type: 'custom',
    dynamic: {
      inputs: ['a', 'b'],   // two inputs
      outputs: ['sum'],     // one output
    },
    data: {
      label: 'Add',
      dynamic: {
        inputs: ['a', 'b'],
        outputs: ['sum'],
      },
    },
  },
  {
    label: 'Print',
    type: 'custom',
    dynamic: {
      inputs: ['in'],       // single input
    },
    data: {
      label: 'Print',
      dynamic: {
        inputs: ['in'],
      },
    },
  },
];


export default function Sidebar() {
  return (
    <div className="w-full h-full flex flex-col bg-emerald-50/30 border-r-2 border-emerald-100/50 rounded-[22px] overflow-hidden">
      {/* Header - Fixed */}
      <div className="flex-shrink-0 p-4 border-b-2 border-emerald-100/50">
        <h3 className="font-black text-sm uppercase tracking-tight text-emerald-900">
          Node Library
        </h3>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="space-y-2">
          {nodeDefinitions.map((node) => (
            <NodeItem
              key={node.label}
              label={node.label}
              type={node.type}
              nodeData={node.data} // pass the full data with dynamic info
            />
          ))}
        </div>
      </div>
    </div>
  );
}
