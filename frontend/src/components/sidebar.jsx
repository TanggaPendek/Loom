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
    <div className="w-full p-2 h-full border-r border-gray-300 bg-gray-50 rounded-lg shadow-sm">
      <div className="font-bold text-gray-700 mb-2 text-sm">Node Library</div>
      {nodeDefinitions.map((node) => (
        <NodeItem
          key={node.label}
          label={node.label}
          type={node.type}
          nodeData={node.data} // pass the full data with dynamic info
        />
      ))}
    </div>
  );
}
