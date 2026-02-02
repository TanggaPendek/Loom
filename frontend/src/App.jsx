import { useState, useEffect } from "react";
import "./App.css";
import Canvas from "./components/canvas/canvas.jsx";
import Sidebar from "./components/sidebar/Sidebar.jsx";
import Navbar from "./components/navbar/navbar.jsx";
import PropertiesBar from "./components/propertiesBar/propertiesBar.jsx";
import EngineButton from "./components/engine_button.jsx";
import { initProject } from "./api/commands.jsx";
import ProjectModal from "./modal/projectList.jsx";
import { ReactFlowProvider } from "reactflow";
import { Loader2, ChevronLeft, ChevronRight, PanelLeftClose, PanelRightClose } from "lucide-react";

function App() {
  const [activeProject, setActiveProject] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [selectedElement, setSelectedElement] = useState(null);
  const [refreshCanvas, setRefreshCanvas] = useState(null);
  const [isWeaving, setIsWeaving] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [propertiesCollapsed, setPropertiesCollapsed] = useState(false);
  const [canvasEdges, setCanvasEdges] = useState([]); // Store edges from Canvas

  useEffect(() => {
    initProject().then((data) => {
      console.log("Backend Initialized:", data);
    });
  }, []);

  const handleProjectSelected = async (project) => {
    setIsWeaving(true);
    setActiveProject(project);

    try {
      if (refreshCanvas) {
        await refreshCanvas();
      }
    } finally {
      setTimeout(() => setIsWeaving(false), 300);
      setIsModalOpen(false);
    }
  };

  const handleSelect = (element) => {
    console.log("Selected:", element);
    setSelectedElement(element);
  };

  // Calculate grid template columns based on collapse state
  const gridColumns = `${sidebarCollapsed ? '40px' : '260px'} 1fr ${propertiesCollapsed ? '40px' : '300px'}`;

  return (
    <div className="h-screen w-screen flex flex-col bg-[#F8FAF9] relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-emerald-200/30 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-emerald-50/50 rounded-full blur-[100px]" />
      </div>

      {isWeaving && (
        <div className="absolute inset-0 z-[1000] flex flex-col items-center justify-center bg-white/60 backdrop-blur-md transition-opacity duration-300">
          <div className="flex flex-col items-center animate-pulse">
            <Loader2 className="w-10 h-10 text-emerald-500 animate-spin mb-2" />
            <span className="text-[10px] font-bold tracking-[0.3em] text-emerald-800 uppercase">
              Spinning Thread...
            </span>
          </div>
        </div>
      )}

      {isModalOpen && (
        <ProjectModal
          onClose={() => setIsModalOpen(false)}
          onSelectProject={handleProjectSelected}
          refreshCanvas={refreshCanvas}
        />
      )}

      <Navbar onOpenProjectManager={() => setIsModalOpen(true)} />

      <div
        className="flex-1 grid overflow-hidden relative z-10 transition-all duration-300"
        style={{ gridTemplateColumns: gridColumns }}
      >
        {/* LEFT SIDEBAR */}
        <aside className="relative border-r border-emerald-100/20 bg-[#1A1C1B]/95 backdrop-blur-md overflow-hidden">
          {!sidebarCollapsed ? (
            <>
              <div className="h-full overflow-y-auto">
                <Sidebar />
              </div>
              <button
                onClick={() => setSidebarCollapsed(true)}
                className="absolute top-4 right-2 p-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 rounded-lg transition-all"
                title="Collapse sidebar"
              >
                <PanelLeftClose size={16} />
              </button>
            </>
          ) : (
            <button
              onClick={() => setSidebarCollapsed(false)}
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 p-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 rounded-lg transition-all"
              title="Expand sidebar"
            >
              <ChevronRight size={20} />
            </button>
          )}
        </aside>

        {/* MAIN CANVAS */}
        <main className="p-6 overflow-hidden flex flex-col bg-transparent">
          <div className="flex-1 border border-emerald-100/50 shadow-2xl shadow-emerald-900/5 rounded-3xl bg-white/80 backdrop-blur-sm overflow-hidden relative">
            <ReactFlowProvider>
              <Canvas
                onSelect={(element) => setSelectedElement(element)}
                onRegisterRefresh={setRefreshCanvas}
                onEdgesUpdate={setCanvasEdges} // Get edges from Canvas
              />
            </ReactFlowProvider>
          </div>
        </main>

        {/* RIGHT PROPERTIES BAR */}
        <aside className="relative border-l border-emerald-100/50 bg-white/70 backdrop-blur-md overflow-hidden">
          {!propertiesCollapsed ? (
            <>
              <PropertiesBar
                selectedElement={selectedElement}
                edges={canvasEdges} // Pass edges to PropertiesBar
              />
              <button
                onClick={() => setPropertiesCollapsed(true)}
                className="absolute top-4 left-2 p-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 rounded-lg transition-all z-50"
                title="Collapse properties"
              >
                <PanelRightClose size={16} />
              </button>
            </>
          ) : (
            <button
              onClick={() => setPropertiesCollapsed(false)}
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 p-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 rounded-lg transition-all"
              title="Expand properties"
            >
              <ChevronLeft size={20} />
            </button>
          )}
        </aside>
      </div>
    </div>
  );
}

export default App;
