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
import { Loader2 } from "lucide-react";

function App() {
  const [activeProject, setActiveProject] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [selectedElement, setSelectedElement] = useState(null);
  const [nodesSnapshot, setNodesSnapshot] = useState([]);
  const [refreshCanvas, setRefreshCanvas] = useState(null);
const [isWeaving, setIsWeaving] = useState(false);

  useEffect(() => {
    initProject().then((data) => {
      console.log("Backend Initialized:", data);
    });
  }, []);

const handleProjectSelected = async (project) => {
    setIsWeaving(true); // Start the "curtain"
    setActiveProject(project);
    
    try {
      // Trigger your version of refresh
      if (refreshCanvas) {
        await refreshCanvas(); 
      }
    } finally {
      // Small timeout ensures the React Flow render cycle completes 
      // so you don't see the "jump"
      setTimeout(() => setIsWeaving(false), 300);
      setIsModalOpen(false);
    }
  };

  const handleSelect = (element) => {
    console.log("Selected:", element);
    setSelectedElement(element);
  };

  const onInputChange = (nodeId, index, val) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          const nextInputs = [...node.data.inputs];
          nextInputs[index] = { ...nextInputs[index], value: val };
          return { ...node, data: { ...node.data, inputs: nextInputs } };
        }
        return node;
      }),
    );
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#F8FAF9] relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-emerald-200/30 rounded-full blur-[120px]" />

        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-emerald-50/50 rounded-full blur-[100px]" />
      </div>
      <svg style={{ position: "absolute", width: 0, height: 0 }}>
        <filter
          id="cotton-fiber-filter"
          x="-20%"
          y="-20%"
          width="140%"
          height="140%"
        >
          {/* High frequency noise creates the "hairs" */}
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.8"
            numOctaves="4"
            result="noise"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="noise"
            scale="1.5"
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>
      </svg>
      ;

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
        className="flex-1 grid overflow-hidden relative z-10"
        style={{ gridTemplateColumns: "260px 1fr 300px" }}
      >
        <aside className="border-r border-emerald-100/20 bg-[#1A1C1B]/95 backdrop-blur-md overflow-y-auto">
          <Sidebar />
        </aside>

        <main className="p-6 overflow-hidden flex flex-col bg-transparent">
          <div className="flex-1 border border-emerald-100/50 shadow-2xl shadow-emerald-900/5 rounded-3xl bg-white/80 backdrop-blur-sm overflow-hidden relative">
            <ReactFlowProvider>
              <Canvas
                onSelect={(element) => setSelectedElement(element)}
                onRegisterRefresh={setRefreshCanvas}
              />
            </ReactFlowProvider>
          </div>
        </main>

        <aside className="border-l border-emerald-100/50 bg-white/70 backdrop-blur-md">
          <PropertiesBar
            selectedElement={selectedElement}
            onUpdateValue={(idx, val) =>
              onInputChange(selectedElement.id, idx, val)
            }
          />
        </aside>
      </div>
    </div>
  );
}

export default App;
