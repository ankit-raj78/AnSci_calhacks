import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DocumentUpload from './DocumentUpload';
import QueryInterface from './QueryInterface';
import './WorkspaceView.css';

function WorkspaceView({ workspace, onBack }) {
  const [documents, setDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState('documents');
  const [currentQuery, setCurrentQuery] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, [workspace.id]);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`/api/workspaces/${workspace.id}/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleFileUpload = async (file, docType) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);

    try {
      const response = await axios.post(
        `/api/workspaces/${workspace.id}/upload`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      fetchDocuments();
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Upload error:', error);
      return { success: false, error: error.message };
    }
  };

  const handleSubmitQuery = async (query) => {
    try {
      const response = await axios.post(
        `/api/workspaces/${workspace.id}/query`,
        { query }
      );
      setCurrentQuery(response.data);
      setActiveTab('analysis');
      return response.data;
    } catch (error) {
      console.error('Query error:', error);
      throw error;
    }
  };

  const handleApproveQuery = async (queryId, action) => {
    try {
      const response = await axios.post(
        `/api/queries/${queryId}/approve`,
        { action }
      );
      setCurrentQuery({ ...currentQuery, ...response.data });
      return response.data;
    } catch (error) {
      console.error('Approval error:', error);
      throw error;
    }
  };

  const handleRefineQuery = async (queryId, feedback) => {
    try {
      const response = await axios.post(
        `/api/queries/${queryId}/refine`,
        { feedback }
      );
      setCurrentQuery({ ...currentQuery, ...response.data, status: 'pending' });
      return response.data;
    } catch (error) {
      console.error('Refine error:', error);
      throw error;
    }
  };

  return (
    <div className="workspace-view">
      <div className="workspace-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Workspaces
        </button>
        <h2>{workspace.name}</h2>
      </div>

      <div className="workspace-tabs">
        <button 
          className={activeTab === 'documents' ? 'active' : ''}
          onClick={() => setActiveTab('documents')}
        >
          Documents ({documents.length})
        </button>
        <button 
          className={activeTab === 'analysis' ? 'active' : ''}
          onClick={() => setActiveTab('analysis')}
        >
          Analysis
        </button>
      </div>

      <div className="workspace-content">
        {activeTab === 'documents' ? (
          <div className="documents-section">
            <DocumentUpload onUpload={handleFileUpload} />
            
            <div className="documents-list">
              <h3>Uploaded Documents</h3>
              {documents.length === 0 ? (
                <p className="empty-state">No documents uploaded yet</p>
              ) : (
                <div className="document-grid">
                  {documents.map(doc => (
                    <div key={doc.id} className="document-card">
                      <div className="doc-icon">📄</div>
                      <h4>{doc.filename}</h4>
                      <p className="doc-type">{doc.doc_type}</p>
                      <p className="doc-date">
                        {new Date(doc.uploaded_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          <QueryInterface
            currentQuery={currentQuery}
            onSubmitQuery={handleSubmitQuery}
            onApproveQuery={handleApproveQuery}
            onRefineQuery={handleRefineQuery}
            hasDocuments={documents.length > 0}
          />
        )}
      </div>
    </div>
  );
}

export default WorkspaceView; 