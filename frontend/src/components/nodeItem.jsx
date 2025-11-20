import React, { useState, useEffect } from 'react';

export default function NodeItem({ label, nodeData }) {
  const [bgColor, setBgColor] = useState('');

  useEffect(() => {
    const hue = Math.floor(Math.random() * 360);
    const sat = Math.floor(Math.random() * 30) + 70; // 70-100%
    const light = Math.floor(Math.random() * 20) + 70; // 70-90%
    setBgColor(`hsl(${hue}, ${sat}%, ${light}%)`);
  }, []);

  return (
    <div
      className="p-3 mb-2 rounded-lg border border-gray-300 shadow-sm cursor-pointer transition transform hover:scale-105 duration-200 text-center font-medium text-gray-800"
      style={{ backgroundColor: bgColor }}
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData('application/reactflow', JSON.stringify(nodeData));
        e.dataTransfer.effectAllowed = 'move';
      }}
    >
      {label}
    </div>
  );
}
