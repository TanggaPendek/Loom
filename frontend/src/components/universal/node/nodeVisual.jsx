import React from 'react';
import NodeDynamic from './nodeDynamic';

export default function NodeVisual({ data, showHandles, isMini }) {
  const isActionNode = data.type === 'trigger' || data.type === 'delete';
  
  // High-Contrast Mapping
  const theme = isActionNode 
    ? { accent: 'bg-rose-500', text: 'text-rose-600', shadow: 'shadow-rose-200/40', border: 'border-rose-100' }
    : { accent: 'bg-emerald-500', text: 'text-emerald-700', shadow: 'shadow-emerald-200/40', border: 'border-emerald-100' };

  return (
    <div 
      className={`
        relative group transition-all duration-300 active:scale-95
        bg-[#FCFDFB] border-2 ${theme.border}
        ${isMini ? 'p-3 w-full rounded-[20px]' : 'p-6 min-w-[200px] rounded-[24px]'} 
        shadow-[0_8px_30px_rgb(0,0,0,0.04)] ${theme.shadow}
        hover:translate-y-[-2px]
      `}
    >
      {/* 1. THE CONTRAST BAR: Anchors the organic shape with a hard professional line */}
      <div className={`absolute left-0 top-0 bottom-0 w-1.5 ${theme.accent} rounded-l-[24px]`} />

      {/* 2. THE TEXTURE: Slightly more visible for "Handmade" grit */}
      <div 
        className="absolute inset-0 pointer-events-none opacity-10" 
        style={{ filter: 'url(#cotton-texture)', mixBlendMode: 'multiply' }} 
      />

      <div className="relative z-10 flex flex-col gap-1">
        {/* 3. AUTHORITATIVE TYPOGRAPHY: Heavier weight and higher contrast text */}
        <header className="flex justify-between items-start">
          <span className={`font-black text-[10px] uppercase tracking-[0.25em] ${theme.text}`}>
            {data.name || data.label}
          </span>
          
          {/* High-Contrast Badge for Mini version */}
          {isMini && (
            <div className={`w-2 h-2 rounded-full ${theme.accent} shadow-sm`} />
          )}
        </header>

        {/* 4. CONTENT GUTS */}
        {!isMini ? (
          <div className="mt-4 p-4 bg-white/50 backdrop-blur-sm rounded-[16px] border border-emerald-50">
            <NodeDynamic data={data} showHandles={showHandles} />
          </div>
        ) : (
          <div className="text-[11px] font-medium leading-relaxed text-slate-700 line-clamp-2 mt-1">
            {data.metadata?.description || "Modular Node Unit"}
          </div>
        )}
      </div>

      {/* 5. TACTILE HOVER OVERLAY */}
      <div className="absolute inset-0 border-2 border-transparent group-hover:border-emerald-500/10 rounded-[24px] pointer-events-none transition-colors" />
    </div>
  );
}