import React, { useState, useEffect } from 'react';
import { request, get } from '../../api/commands'; // Adjust path as needed

const ProjectManager = ({ isOpen, onClose, onProjectSelect }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch projects from backend
  const fetchProjects = async () => {
    setLoading(true);
    const data = await get("/sync/projects"); // Assuming this endpoint exists
    if (data) setProjects(data);
    setLoading(false);
  };

  useEffect(() => {
    if (isOpen) fetchProjects();
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-[#252526] w-[500px] rounded-lg shadow-2xl border border-gray-700 flex flex-col max-h-[80vh]">
        
        <header className="p-4 border-b border-gray-700 flex justify-between items-center">
          <h2 className="text-white font-semibold">Project Manager</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">✕</button>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {projects.length === 0 ? (
            <p className="text-gray-500 text-center py-10">No projects found.</p>
          ) : (
            projects.map((proj) => (
              <div 
                key={proj.id} 
                className="group flex items-center justify-between p-3 rounded bg-[#2d2d2d] hover:bg-[#37373d] border border-transparent hover:border-blue-500 cursor-pointer transition-all"
                onClick={() => onProjectSelect(proj)}
              >
                <div>
                  <div className="text-gray-200 font-medium">{proj.name}</div>
                  <div className="text-xs text-gray-500">Last modified: {proj.updatedAt}</div>
                </div>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    if(confirm("Delete project?")) console.log("Delete", proj.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-2 text-red-400 hover:bg-red-900/20 rounded"
                >
                  🗑️
                </button>
              </div>
            ))
          )}
        </div>

        <footer className="p-4 border-t border-gray-700 bg-[#1e1e1e] flex justify-end gap-3">
          <button 
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded"
          >
            Cancel
          </button>
          <button 
            className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded font-medium"
            onClick={() => console.log("Trigger Create Project API")}
          >
            + New Project
          </button>
        </footer>
      </div>
    </div>
  );
};

export default ProjectManager;