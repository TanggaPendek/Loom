// Navbar.jsx
import React, { useState } from "react";
import { NAVBAR_MENU } from "./navbarConfig";

const Navbar = ({ onOpenProjectManager }) => {
  const [activeMenu, setActiveMenu] = useState(null);

  const handleAction = (actionId) => {
    setActiveMenu(null);
    if (actionId === "change" || actionId === "new") {
      onOpenProjectManager();
    }
    if (actionId === "save") {
      console.log("Saving...");
    }
  };

  return (
    <nav className="bg-gray-900 text-gray-200 px-4 py-2 flex justify-between items-center shadow-md">
      <div className="flex items-center gap-4">
        <span className="text-lg font-semibold">Loom</span>
        {NAVBAR_MENU.map((menu) => (
          <div key={menu.id} className="relative">
            <button
              onClick={() =>
                setActiveMenu(activeMenu === menu.id ? null : menu.id)
              }
              className="px-3 py-1 rounded hover:bg-gray-700 hover:text-white transition-colors"
            >
              {menu.label}
            </button>

            {/* Dropdown Menu */}
            {activeMenu === menu.id && (
              <div className="absolute left-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded shadow-lg z-50">
                {menu.items.map((item, index) =>
                  item.type === "divider" ? (
                    <div key={index} className="border-t border-gray-600 my-1" />
                  ) : (
                    <button
                      key={item.id}
                      onClick={() => handleAction(item.id)}
                      className={`w-full text-left px-4 py-2 hover:bg-blue-600 hover:text-white flex justify-between items-center ${
                        item.variant === "danger" ? "text-red-400" : ""
                      }`}
                    >
                      <span>{item.label}</span>
                      {item.icon && <span className="opacity-50 text-xs">{item.icon}</span>}
                    </button>
                  )
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </nav>
  );
};

export default Navbar;
