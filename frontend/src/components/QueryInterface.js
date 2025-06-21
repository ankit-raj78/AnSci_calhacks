import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './QueryInterface.css';

function QueryInterface({ 
  currentQuery, 
  onSubmitQuery, 
  onApproveQuery, 
  onRefineQuery,
  hasDocuments 
}) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      await onSubmitQuery(query);
      setQuery('');
    } catch (error) {
      console.error('Query submission error:', error);
    }
    setLoading(false);
  };

  const handleApprove = async (action) => {
    if (action === 'reject') {
      setShowFeedbackForm(true);
      return;
    }

    setLoading(true);
    try {
      await onApproveQuery(currentQuery.id, action);
    } catch (error) {
      console.error('Approval error:', error);
    }
    setLoading(false);
  };

  const handleRefine = async (e) => {
    e.preventDefault();
    if (!feedback.trim()) return;

    setLoading(true);
    try {
      await onRefineQuery(currentQuery.id, feedback);
      setFeedback('');
      setShowFeedbackForm(false);
    } catch (error) {
      console.error('Refine error:', error);
    }
    setLoading(false);
  };

  if (!hasDocuments) {
    return (
      <div className="query-interface">
        <div className="empty-state">
          <h3>No documents uploaded yet</h3>
          <p>Please upload survey designs and data files first before making queries.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="query-interface">
      <div className="query-form-section">
        <h3>Ask a Question</h3>
        <form onSubmit={handleSubmit}>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="E.g., 'Analyze the satisfaction scores by age group' or 'What are the main themes in the open-ended responses?'"
            rows={4}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !query.trim()}>
            {loading ? 'Processing...' : 'Submit Query'}
          </button>
        </form>
      </div>

      {currentQuery && (
        <div className="query-result">
          <div className="query-header">
            <h3>Analysis Plan</h3>
            <span className={`status-badge ${currentQuery.status}`}>
              {currentQuery.status}
            </span>
          </div>

          <div className="plan-section">
            <h4>Proposed Plan:</h4>
            <pre>{currentQuery.plan}</pre>
          </div>

          <div className="code-section">
            <h4>Generated Code:</h4>
            <SyntaxHighlighter 
              language="python" 
              style={vscDarkPlus}
              customStyle={{
                maxHeight: '400px',
                fontSize: '14px'
              }}
            >
              {currentQuery.code}
            </SyntaxHighlighter>
          </div>

          {currentQuery.status === 'pending' && !showFeedbackForm && (
            <div className="approval-actions">
              <h4>Do you approve this analysis plan?</h4>
              <button 
                className="approve-btn"
                onClick={() => handleApprove('approve')}
                disabled={loading}
              >
                ✓ Approve & Execute
              </button>
              <button 
                className="reject-btn"
                onClick={() => handleApprove('reject')}
                disabled={loading}
              >
                ✗ Reject & Refine
              </button>
            </div>
          )}

          {showFeedbackForm && (
            <div className="feedback-form">
              <h4>Provide Feedback for Refinement</h4>
              <form onSubmit={handleRefine}>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Explain what needs to be changed or improved..."
                  rows={3}
                  autoFocus
                />
                <div className="feedback-actions">
                  <button 
                    type="button" 
                    onClick={() => {
                      setShowFeedbackForm(false);
                      setFeedback('');
                    }}
                  >
                    Cancel
                  </button>
                  <button type="submit" disabled={loading || !feedback.trim()}>
                    {loading ? 'Refining...' : 'Submit Feedback'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {currentQuery.result && (
            <div className="execution-result">
              <h4>Execution Result:</h4>
              <pre className={currentQuery.status === 'executed' ? 'success' : 'error'}>
                {currentQuery.result}
              </pre>
            </div>
          )}
        </div>
      )}

      <div className="query-examples">
        <h4>Example Queries:</h4>
        <ul>
          <li>"What is the overall satisfaction score and how does it vary by demographic groups?"</li>
          <li>"Identify the top 5 issues mentioned in customer feedback"</li>
          <li>"Create a correlation matrix of all survey questions"</li>
          <li>"Analyze response rates and identify any patterns in missing data"</li>
        </ul>
      </div>
    </div>
  );
}

export default QueryInterface; 