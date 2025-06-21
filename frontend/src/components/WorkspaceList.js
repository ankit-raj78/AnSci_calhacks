import React, { useState } from 'react';
import './WorkspaceList.css';

function WorkspaceList({ workspaces, onSelectWorkspace, onCreateWorkspace, loading }) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = useState('');

  const handleCreate = async (e) => {
    e.preventDefault();
    if (newWorkspaceName.trim()) {
      await onCreateWorkspace(newWorkspaceName);
      setNewWorkspaceName('');
      setShowCreateForm(false);
    }
  };

  return (
    <div className="workspace-list">
      <h2>Your Workspaces</h2>
      
      <div className="workspace-grid">
        {workspaces.map(workspace => (
          <div 
            key={workspace.id} 
            className="workspace-card"
            onClick={() => onSelectWorkspace(workspace)}
          >
            <h3>{workspace.name}</h3>
            <p>Created: {new Date(workspace.created_at).toLocaleDateString()}</p>
          </div>
        ))}
        
        <div 
          className="workspace-card create-new"
          onClick={() => setShowCreateForm(true)}
        >
          <div className="plus-icon">+</div>
          <p>Create New Workspace</p>
        </div>
      </div>

      {showCreateForm && (
        <div className="modal-overlay" onClick={() => setShowCreateForm(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Create New Workspace</h3>
            <form onSubmit={handleCreate}>
              <input
                type="text"
                placeholder="Workspace name"
                value={newWorkspaceName}
                onChange={(e) => setNewWorkspaceName(e.target.value)}
                autoFocus
                required
              />
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateForm(false)}>
                  Cancel
                </button>
                <button type="submit" disabled={loading}>
                  {loading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default WorkspaceList; 