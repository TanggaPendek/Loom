import React, { useState, useEffect } from "react";
import DynamicNode from "./dynamicNode";

export default function NodeVisual({ data }) {
  const [hovered, setHovered] = useState(false);
  const [bgColor, setBgColor] = useState("");

  useEffect(() => {
    const hue = Math.floor(Math.random() * 360);
    const saturation = Math.floor(Math.random() * 30) + 70;
    const lightness = Math.floor(Math.random() * 20) + 70;
    setBgColor(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
  }, []);

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className={`p-3 rounded-xl text-center font-medium cursor-pointer min-w-[120px] transition-all duration-300 
        ${hovered ? "border-2 border-indigo-400 shadow-xl" : "border border-gray-300 shadow-md"}`}
      style={{ backgroundColor: bgColor, color: "#1e293b" }}
    >
      <div className="mb-2">{data.label}</div>

      {/* Render DynamicNode if it has any inputs, outputs, or controls */}
      {data.dynamic &&
        (data.dynamic.inputs?.length > 0 ||
          data.dynamic.outputs?.length > 0 ||
          data.dynamic.controls?.length > 0) && (
          <DynamicNode data={data.dynamic} />
        )}
    </div>
  );
}
