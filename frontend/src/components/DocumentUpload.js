import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import './DocumentUpload.css';

function DocumentUpload({ onUpload }) {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    setUploading(true);
    setUploadStatus(null);

    for (const file of acceptedFiles) {
      // Determine document type based on file name or ask user
      const docType = file.name.toLowerCase().includes('design') ? 'survey_design' : 'data';
      
      const result = await onUpload(file, docType);
      
      if (result.success) {
        setUploadStatus({
          type: 'success',
          message: `Successfully uploaded ${file.name}`
        });
      } else {
        setUploadStatus({
          type: 'error',
          message: `Failed to upload ${file.name}: ${result.error}`
        });
      }
    }

    setUploading(false);
    
    // Clear status after 3 seconds
    setTimeout(() => setUploadStatus(null), 3000);
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/json': ['.json']
    },
    multiple: true
  });

  return (
    <div className="document-upload">
      <h3>Upload Documents</h3>
      
      <div 
        {...getRootProps()} 
        className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'uploading' : ''}`}
      >
        <input {...getInputProps()} />
        
        {uploading ? (
          <div className="upload-progress">
            <div className="spinner"></div>
            <p>Uploading...</p>
          </div>
        ) : isDragActive ? (
          <p>Drop the files here...</p>
        ) : (
          <>
            <div className="upload-icon">📤</div>
            <p>Drag & drop files here, or click to select</p>
            <p className="file-types">
              Supported: CSV, Excel, PDF, TXT, JSON
            </p>
          </>
        )}
      </div>

      {uploadStatus && (
        <div className={`upload-status ${uploadStatus.type}`}>
          {uploadStatus.message}
        </div>
      )}

      <div className="upload-tips">
        <h4>Tips:</h4>
        <ul>
          <li>Upload survey design documents (questionnaires, methodologies)</li>
          <li>Upload survey data files (responses, results)</li>
          <li>Files with "design" in the name will be marked as survey designs</li>
          <li>All other files will be marked as data files</li>
        </ul>
      </div>
    </div>
  );
}

export default DocumentUpload; 