import React, { useEffect, useState } from "react";
import {
  getStartupData,
  createProject,
  deleteProject,
  selectProject,
} from "../api/commands";
import { Trash2, Plus, Sprout, X, Loader2, Sparkles } from "lucide-react";

const ProjectModal = ({ onSelectProject, onClose, refreshCanvas }) => {

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newProjectName, setNewProjectName] = useState("");


  const refreshProjects = async () => {
    setLoading(true);
    try {
      const data = await getStartupData();
      setProjects(data?.project_index || []);
    } catch (err) {
      console.error("Failed to fetch projects", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshProjects();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    await createProject({ projectName: newProjectName });
    setNewProjectName("");
    refreshProjects();
  };

const handleProjectClick = async (proj) => {
  await selectProject(proj.projectId).catch(() => {});

  if (onSelectProject) {
    await onSelectProject(proj); 
  }
};


  return (
    <div className="fixed inset-0 z-[999] flex items-center justify-center p-4 bg-emerald-950/20 backdrop-blur-md">
      {/* Texture: Cotton / Grain */}
      <div
        className="absolute inset-0 opacity-[0.05] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.6'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
        }}
      ></div>

      {/* Modal Card */}
      <div className="relative bg-[#FCFDFB] w-full max-w-lg rounded-[32px] shadow-[0_30px_70px_-10px_rgba(50,80,50,0.2)] border border-emerald-100 overflow-hidden flex flex-col">
        {/* Header: Sage to Pink Gradient */}
        <div className="px-8 py-7 flex justify-between items-center bg-gradient-to-br from-[#f2f7f2] via-white to-[#fdf2f5] border-b border-emerald-50">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500 rounded-2xl shadow-sm ring-4 ring-emerald-50">
              <Sprout className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-800 tracking-tight leading-none">
                Switch Space
              </h2>
              <p className="text-[10px] text-emerald-600 font-bold uppercase tracking-widest mt-1">
                Personal Workspace
              </p>
            </div>
          </div>

          {/* CONTRAST CLOSE BUTTON: Pink & Solid White Background */}
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              if (onClose) onClose();
            }}
            className="group relative p-3 rounded-2xl bg-white text-pink-500 shadow-md hover:bg-pink-500 hover:text-white transition-all duration-300 border border-pink-100 active:scale-90"
            aria-label="Close"
          >
            <X className="w-6 h-6 stroke-[3px]" />
            {/* Tooltip kecil bila hover (optional) */}
            <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
              Close
            </span>
          </button>
        </div>

        {/* Project List */}
        <div className="max-h-[350px] overflow-y-auto px-6 py-4 space-y-3 bg-[#FCFDFB]">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-300" />
            </div>
          ) : (
            projects.map((proj) => (
              <div
                key={proj.projectId}
                onClick={() => handleProjectClick(proj)}
                className="group flex items-center justify-between p-5 rounded-[24px] cursor-pointer bg-white border border-emerald-50 hover:border-emerald-200 hover:bg-emerald-50/20 transition-all duration-300 hover:shadow-sm"
              >
                <div className="flex flex-col">
                  <span className="text-base font-semibold text-slate-700 group-hover:text-emerald-800 transition-colors">
                    {proj.projectName}
                  </span>
                  <span className="text-[10px] text-slate-400 font-medium uppercase mt-1">
                    Last edited{" "}
                    {new Date(proj.lastModified).toLocaleDateString()}
                  </span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm("Delete?"))
                      deleteProject(proj.projectId).then(refreshProjects);
                  }}
                  className="p-2 text-slate-200 hover:text-red-400 hover:bg-red-50 rounded-xl transition-all"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>

        {/* Footer: Inline Create Action */}
        <div className="p-8 bg-[#f9fbf9] border-t border-emerald-50">
          <form onSubmit={handleCreate} className="flex flex-col gap-4">
            <div className="relative group">
              <input
                type="text"
                placeholder="Name your new project..."
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                className="w-full px-6 py-4 rounded-2xl bg-white border border-emerald-100 focus:border-pink-300 focus:ring-4 focus:ring-pink-50 outline-none transition-all text-slate-700 font-medium placeholder:text-slate-300"
              />
              <Sparkles className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-emerald-100 group-focus-within:text-pink-300 transition-colors" />
            </div>

            <button
              type="submit"
              disabled={!newProjectName.trim()}
              className="w-full flex items-center justify-center gap-2 py-4 rounded-[20px] bg-emerald-500 hover:bg-pink-500 text-white font-bold text-xs tracking-[0.2em] transition-all duration-500 shadow-lg shadow-emerald-100 hover:shadow-pink-100 uppercase disabled:opacity-30"
            >
              <Plus className="w-4 h-4 stroke-[3px]" />
              Create Project
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProjectModal;
