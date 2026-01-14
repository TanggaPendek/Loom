import { useState, useEffect } from "react";
import "./App.css";
import Canvas from "./components/canvas/canvas.jsx";
import Sidebar from "./components/sidebar/Sidebar.jsx";
import Navbar from "./components/navbar/navbar.jsx";
import PropertiesBar from "./components/propertiesBar/propertiesBar.jsx";
import EngineButton from "./components/engine_button.jsx";
import { initProject } from "./api/commands.jsx";
import ProjectModal from "./modal/projectList.jsx";

function App() {
  // 1. Initialize to true so it shows immediately on load
  const [showModal, setShowModal] = useState(true);
  const [refreshCanvas, setRefreshCanvas] = useState(() => () => {});

  useEffect(() => {
    initProject().then((data) => {
      console.log("Backend Initialized:", data);
    });
  }, []);

  const handleProjectSelected = (project) => {
    setActiveProject(project);
    setShowModal(false);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-900">
      {/* 0. FORCE POPUP - Overlaying the entire app */}
      {showModal && (
        <ProjectModal
          onSuccess={() => {
            setShowModal(false);
            refreshCanvas(); // 👈 direct “yo refresh”
          }}
        />
      )}

      {/* 1. TOP NAVBAR */}
      <Navbar />

      {/* 2. MAIN CONTENT AREA */}
      <div
        className="flex-1 grid overflow-hidden"
        style={{ gridTemplateColumns: "260px 1fr 300px" }}
      >
        {/* Left Sidebar */}
        <aside className="border-r border-gray-700 bg-[#252526] overflow-y-auto">
          <Sidebar />
        </aside>

        {/* Main Canvas Area */}
        <main className="bg-gray-100 p-4 overflow-hidden flex flex-col">
          <div className="flex-1 border border-gray-300 shadow-inner rounded-lg bg-white overflow-hidden relative">
            <Canvas onRegisterRefresh={setRefreshCanvas} />
          </div>
        </main>

        {/* Right Sidebar (Properties) */}
        <aside className="border-l border-gray-700 bg-white">
          <PropertiesBar />
          <div className="px-4 pb-4">
            <EngineButton />
          </div>
        </aside>
      </div>
    </div>
  );
}

export default App;
