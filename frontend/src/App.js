import React, { useState, useEffect } from 'react';
import axios from 'axios';
import WorkspaceList from './components/WorkspaceList';
import WorkspaceView from './components/WorkspaceView';
import './App.css';

function App() {
  const [workspaces, setWorkspaces] = useState([]);
  const [selectedWorkspace, setSelectedWorkspace] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchWorkspaces();
  }, []);

  const fetchWorkspaces = async () => {
    try {
      const response = await axios.get('/api/workspaces');
      setWorkspaces(response.data);
    } catch (error) {
      console.error('Error fetching workspaces:', error);
    }
  };

  const createWorkspace = async (name) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/workspaces', { name });
      setWorkspaces([...workspaces, response.data]);
      setLoading(false);
    } catch (error) {
      console.error('Error creating workspace:', error);
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Survey Analysis Platform</h1>
        <p>Upload survey designs and data, ask questions, and get AI-powered analysis</p>
      </header>
      
      <div className="App-content">
        {!selectedWorkspace ? (
          <WorkspaceList 
            workspaces={workspaces}
            onSelectWorkspace={setSelectedWorkspace}
            onCreateWorkspace={createWorkspace}
            loading={loading}
          />
        ) : (
          <WorkspaceView 
            workspace={selectedWorkspace}
            onBack={() => setSelectedWorkspace(null)}
          />
        )}
      </div>
    </div>
  );
}

export default App; 