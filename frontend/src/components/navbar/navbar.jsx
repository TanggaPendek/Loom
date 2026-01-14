import React, { useState } from "react";
import { NAVBAR_MENU } from "./navbarConfig";

const Navbar = () => {
  const [activeMenu, setActiveMenu] = useState(null);

  const handleAction = (actionId) => {
    setActiveMenu(null);
    if (actionId === "change" || actionId === "new") {
      onOpenProjectManager(); // Trigger the modal
    }
    if (actionId === "save") {
      // Direct API Call
      console.log("Saving...");
    }
  };

  return (
    <nav className="h-12 border-b border-gray-700 bg-[#1e1e1e] flex items-center px-4 text-gray-300 relative z-50">
      <div className="flex items-center gap-2">
        {NAVBAR_MENU.map((menu) => (
          <div key={menu.id} className="relative">
            <button
              onClick={() =>
                setActiveMenu(activeMenu === menu.id ? null : menu.id)
              }
              className={`px-3 py-1 rounded hover:bg-gray-700 hover:text-white transition-colors ${
                activeMenu === menu.id ? "bg-gray-700 text-white" : ""
              }`}
            >
              {menu.label}
            </button>

            {/* Dropdown Menu */}
            {activeMenu === menu.id && (
              <div className="absolute left-0 mt-1 w-48 bg-[#2d2d2d] border border-gray-700 rounded shadow-xl py-1 text-sm">
                {menu.items.map((item, index) =>
                  item.type === "divider" ? (
                    <div
                      key={index}
                      className="border-t border-gray-600 my-1"
                    />
                  ) : (
                    <button
                      key={item.id}
                      onClick={() => handleAction(item.id)}
                      className={`w-full text-left px-4 py-2 flex justify-between items-center hover:bg-blue-600 hover:text-white ${
                        item.variant === "danger" ? "text-red-400" : ""
                      }`}
                    >
                      <span>{item.label}</span>
                      <span className="opacity-50 text-xs">{item.icon}</span>
                    </button>
                  )
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Background click listener to close dropdown */}
      {activeMenu && (
        <div
          className="fixed inset-0 z-[-1]"
          onClick={() => setActiveMenu(null)}
        />
      )}
    </nav>
  );
};

export default Navbar;
