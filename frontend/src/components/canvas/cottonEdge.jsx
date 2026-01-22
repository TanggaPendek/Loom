import React, { useMemo } from "react";
import { BaseEdge, getBezierPath } from "reactflow";

export default function CottonEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
}) {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  // Generate unique fiber patterns once per edge so they don't "flicker"
  const fiberStyles = useMemo(() => {
    return [...Array(3)].map((_, i) => ({
      strokeWidth: 0.5 + i * 0.5,
      dashArray: `${5 + i * 2} ${10 + i * 5}`,
      opacity: 0.3 - i * 0.05,
      offset: (i - 1) * 0.8, // Slight offset to make it look "frayed"
    }));
  }, []);

  return (
    <>
      <defs>
        {/* A custom filter to give it that organic cotton bleed */}
        <filter id="cotton-fuzz" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="0.8" result="blur" />
          <feTurbulence type="fractalNoise" baseFrequency="0.5" numOctaves="3" result="noise" />
          <feDisplacementMap in="blur" in2="noise" scale="2" xChannelSelector="R" yChannelSelector="G" />
        </filter>
      </defs>

      {/* 1. OUTER HALO (The Fuzz) */}
      <BaseEdge
        path={edgePath}
        style={{
          stroke: "#D1FAE5",
          strokeWidth: 8,
          opacity: 0.15,
          filter: "url(#cotton-fuzz)",
        }}
      />

      {/* 2. STRAY SPUN FIBERS (Stable) */}
      {fiberStyles.map((fiber, i) => (
        <BaseEdge
          key={`${id}-fiber-${i}`}
          path={edgePath}
          style={{
            stroke: "#10B981",
            strokeWidth: fiber.strokeWidth,
            strokeDasharray: fiber.dashArray,
            opacity: fiber.opacity,
            transform: `translate(${fiber.offset}px, ${fiber.offset}px)`,
          }}
        />
      ))}

      {/* 3. THE CORE THREAD */}
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          stroke: "#059669", // Slightly darker for depth
          strokeWidth: 1.5,
          strokeLinecap: "round",
          ...style,
        }}
      />
    </>
  );
}