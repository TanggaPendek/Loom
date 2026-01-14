import React, { useEffect, useState } from 'react';
import { getStartupData, createProject, deleteProject, loadProject, selectProject } from '../api/commands';
import './projectList.css'

const ProjectModal = ({ onSelectProject }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

// Fetch projects on mount
  const refreshProjects = async () => {
    setLoading(true);
    const data = await getStartupData();
    
    // CHANGE: Access .project_index instead of setting the whole object
    if (data && data.project_index) {
      setProjects(data.project_index);
    } else {
      setProjects([]); // Fallback to empty list
    }
    
    setLoading(false);
  };

  useEffect(() => {
    refreshProjects();
  }, []);

  const handleCreate = async () => {
    const name = prompt("Enter project name:");
    if (name) {
      await createProject({ projectName: name });
      refreshProjects();
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation(); // Prevent project selection when clicking delete
    if (window.confirm("Delete this project?")) {
      await deleteProject(id);
      refreshProjects();
    }
  };

const handleProjectClick = async (proj) => {
  const ok = await selectProject(proj.projectId);

  if (ok) {
    onSuccess(); // close modal + refresh canvas
  }
};

  if (loading) return <div className="modal-overlay">Loading Projects...</div>;
return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Open Project</h2>
        <div className="project-list">
          {projects.map((proj) => (
            <div 
              key={proj.projectId} className="project-item" onClick={() => handleProjectClick(proj)}
            >
              <div className="project-info">
                <strong>{proj.projectName}</strong>
                <span>{new Date(proj.lastModified).toLocaleDateString()}</span>
              </div>
              <button 
                className="btn-delete" 
                onClick={(e) => handleDelete(e, proj.projectId)}
              >
                Delete
              </button>
            </div>
          ))}
        </div>

        <div className="modal-footer">
          <button className="btn-create" onClick={handleCreate}>+ New Project</button>
        </div>
      </div>
    </div>
  );
};

export default ProjectModal;