import React, { memo } from 'react';
import { BaseEdge, getBezierPath } from 'reactflow';

const CottonEdge = ({ id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style = {}, markerEnd }) => {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      {/* 1. The "Halo" - use a simple drop-shadow instead of turbulence */}
      <path
        id={id}
        style={{ 
          ...style, 
          strokeWidth: 8, 
          stroke: '#10b981', 
          opacity: 0.1,
          filter: 'blur(3px)' // CSS blur is MUCH faster than SVG feGaussianBlur
        }}
        className="react-flow__edge-path"
        d={edgePath}
      />

      {/* 2. The Main Thread - Use dash-array for a "braided" look (No Filter!) */}
      <path
        style={{ 
          ...style, 
          strokeWidth: 3, 
          stroke: '#10b981',
          strokeDasharray: '2, 1', // This creates the "yarn" texture look
          strokeLinecap: 'round'
        }}
        className="react-flow__edge-path"
        d={edgePath}
        markerEnd={markerEnd}
      />

      {/* 3. The Core - A very thin solid line for definition */}
      <path
        style={{ 
          ...style, 
          strokeWidth: 1, 
          stroke: '#ffffff', 
          opacity: 0.5 
        }}
        className="react-flow__edge-path"
        d={edgePath}
      />
    </>
  );
};

export default memo(CottonEdge);