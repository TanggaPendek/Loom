import React, { createContext, useState, useEffect } from 'react';
import { initProject } from '../api/commands';

export const ProjectContext = createContext();

export const ProjectProvider = ({ children }) => {
  const [projectData, setProjectData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Run this once when the app starts
    initProject()
      .then(data => {
        setProjectData(data.payload); // Assuming backend sends { payload: { ... } }
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to init:", err);
        setLoading(false);
      });
  }, []);

  return (
    <ProjectContext.Provider value={{ projectData, setProjectData, loading }}>
      {children}
    </ProjectContext.Provider>
  );
};