import React from 'react';
import NodeVisual from './nodeVisual';

export default function Node({ data, context = 'canvas' }) {
  // If context is 'sidebar', we disable handles and dragging logic
  const isSidebar = context === 'sidebar';

  const onDragStart = (event) => {
    if (!isSidebar) return;
    event.dataTransfer.setData('application/reactflow', JSON.stringify(data));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div 
      draggable={isSidebar} 
      onDragStart={isSidebar ? onDragStart : undefined}
      className={isSidebar ? "cursor-grab active:cursor-grabbing" : ""}
    >
      <NodeVisual 
        data={data} 
        showHandles={!isSidebar} // Hide ports in the sidebar
        isMini={isSidebar}       // Smaller style for sidebar
      />
    </div>
  );
}