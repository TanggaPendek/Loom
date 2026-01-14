import React from 'react';

const PropertyGroup = ({ label, children }) => (
  <div className="mb-6">
    <h4 className="text-xs font-semibold uppercase text-gray-500 mb-3 tracking-widest">{label}</h4>
    <div className="space-y-3">{children}</div>
  </div>
);

const PropertiesBar = () => {
  return (
    <div className="h-full flex flex-col bg-[#f9fafb] text-gray-800">
      <header className="p-4 border-b border-gray-200">
        <h2 className="font-bold">Properties</h2>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        <PropertyGroup label="Transform">
          <div className="grid grid-cols-3 gap-2">
            <input type="number" placeholder="X" className="border p-1 text-sm rounded" />
            <input type="number" placeholder="Y" className="border p-1 text-sm rounded" />
            <input type="number" placeholder="Z" className="border p-1 text-sm rounded" />
          </div>
        </PropertyGroup>

        <PropertyGroup label="Appearance">
          <div className="flex flex-col gap-2">
            <label className="text-xs">Opacity</label>
            <input type="range" className="w-full" />
          </div>
        </PropertyGroup>
      </div>

      <footer className="p-4 border-t border-gray-200 bg-gray-50">
        {/* Your EngineButton will go here */}
        <p className="text-[10px] text-gray-400 mb-2">System Actions</p>
      </footer>
    </div>
  );
};

export default PropertiesBar;