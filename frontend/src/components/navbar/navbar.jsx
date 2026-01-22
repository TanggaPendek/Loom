import React, { useState } from "react";
import { NAVBAR_MENU } from "./navbarConfig";

const Navbar = ({ onOpenProjectManager }) => {
  const [activeMenu, setActiveMenu] = useState(null);

  const handleAction = (actionId) => {
    setActiveMenu(null);
    if (actionId === "change" || actionId === "new") {
      onOpenProjectManager();
    }
  };

  return (
    // UPDATED: Changed from #FCFDFB to a slightly deeper #F1F5F2 Sage-tinted off-white
    // Added a more pronounced shadow-sm to create separation from the main content
    <nav className="bg-[#F1F5F2]/90 backdrop-blur-xl sticky top-0 px-6 py-4 flex justify-between items-center z-50 border-b border-emerald-100/50 shadow-sm">
      <div className="flex items-center gap-8">
        <span className="text-xl font-bold tracking-tighter text-emerald-700 uppercase">
          Loom
        </span>
        
        <div className="flex gap-2">
          {NAVBAR_MENU.map((menu) => (
            <div key={menu.id} className="relative">
              <button
                onClick={() => setActiveMenu(activeMenu === menu.id ? null : menu.id)}
                className={`px-4 py-2 rounded-2xl font-semibold transition-all active:scale-95
                  ${activeMenu === menu.id 
                    ? "bg-emerald-100 text-emerald-900" 
                    : "text-emerald-900/60 hover:bg-emerald-50/80 hover:text-emerald-900"}
                `}
              >
                {menu.label}
              </button>

              {activeMenu === menu.id && (
                <div className="absolute left-0 mt-3 w-60 bg-white border border-emerald-100/50 rounded-[28px] shadow-2xl shadow-emerald-900/10 p-2 z-50">
                  {menu.items.map((item, index) =>
                    item.type === "divider" ? (
                      <div key={index} className="h-px bg-emerald-50 my-2 mx-2" />
                    ) : (
                      <button
                        key={item.id}
                        onClick={() => handleAction(item.id)}
                        className={`w-full text-left px-4 py-3 rounded-xl transition-all flex justify-between items-center group active:scale-95
                          ${item.variant === "danger" 
                            ? "hover:bg-rose-50 text-rose-600" 
                            : "hover:bg-emerald-600 hover:text-white text-emerald-900"}
                        `}
                      >
                        <span className="font-medium">{item.label}</span>
                        {item.icon && <span className="opacity-40 group-hover:opacity-100">{item.icon}</span>}
                      </button>
                    )
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;