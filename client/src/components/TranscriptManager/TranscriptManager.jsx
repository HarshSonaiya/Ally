import React, { useState, useEffect } from 'react';
import './TranscriptManager.css';

const TranscriptManager = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [email, setEmail] = useState('');
  const [customDuration, setCustomDuration] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [workspaces, setWorkspaces] = useState([]);
  const [selectedWorkspace, setSelectedWorkspace] = useState('');

  useEffect(() => {
    fetchWorkspaces();
  }, []);

  const fetchWorkspaces = async () => {
    try {
      const response = await fetch('/workspace/list');
      const data = await response.json();
      setWorkspaces(data);
    } catch (error) {
      console.error('Failed to fetch workspaces:', error);
      alert('Error fetching workspaces.');
    }
  };

  const handleCreateWorkspace = async () => {
    try {
      const response = await fetch('/workspace/create', { method: 'POST' });
      const newWorkspace = await response.json();
      setWorkspaces([...workspaces, newWorkspace]);
      alert('Workspace created successfully!');
    } catch (error) {
      console.error('Failed to create workspace:', error);
      alert('Error creating workspace.');
    }
  };

  const handleFileUpload = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleGenerateTranscript = async () => {
    if (!selectedFile || !selectedWorkspace) {
      alert('Please upload a file and select a workspace first.');
      return;
    }
    setIsProcessing(true);
    try {
      const transcript = 'Generated transcript content'; // Replace with actual API call
      setTranscript(transcript);
    } catch (error) {
      console.error('Error generating transcript:', error);
    }
    setIsProcessing(false);
  };

  const handleGenerateSummary = async () => {
    if (!transcript) {
      alert('Please generate the transcript first.');
      return;
    }
    setIsProcessing(true);
    try {
      const summary = 'Generated summary content'; // Replace with actual API call
      setSummary(summary);
    } catch (error) {
      console.error('Error generating summary:', error);
    }
    setIsProcessing(false);
  };

  const handleSendSummary = async () => {
    if (!summary || !email) {
      alert('Please generate the summary and provide email addresses.');
      return;
    }
    setIsProcessing(true);
    try {
      alert(`Summary sent to: ${email}`);
    } catch (error) {
      console.error('Error sending email:', error);
    }
    setIsProcessing(false);
  };

  return (
    <div className="transcript-manager">
      <h1>Transcript and Summary Manager</h1>

      {workspaces.length === 0 ? (
        <div>
          <p>No workspaces found. Please create a workspace first.</p>
          <button onClick={handleCreateWorkspace}>Create Workspace</button>
        </div>
      ) : (
        <>
          <div className="section">
            <label htmlFor="workspace-select">Select Workspace:</label>
            <select
              id="workspace-select"
              value={selectedWorkspace}
              onChange={(e) => setSelectedWorkspace(e.target.value)}
            >
              <option value="">Select Workspace</option>
              {workspaces.map((workspace) => (
                <option key={workspace.name} value={workspace.name}>
                  {workspace.name}
                </option>
              ))}
            </select>
          </div>

          {selectedWorkspace && (
            <>
              <div className="section">
                <label htmlFor="file-upload">Upload File:</label>
                <input
                  type="file"
                  id="file-upload"
                  accept=".mp3, .mp4"
                  onChange={handleFileUpload}
                />
              </div>

              <div className="section">
                <button onClick={handleGenerateTranscript} disabled={isProcessing}>
                  {isProcessing ? 'Processing...' : 'Generate Transcript'}
                </button>
                {transcript && (
                  <div>
                    <h3>Transcript:</h3>
                    <textarea readOnly value={transcript}></textarea>
                  </div>
                )}
              </div>

              <div className="section">
                <button onClick={handleGenerateSummary} disabled={isProcessing}>
                  {isProcessing ? 'Processing...' : 'Generate Summary'}
                </button>
                {summary && (
                  <div>
                    <h3>Summary:</h3>
                    <textarea readOnly value={summary}></textarea>
                  </div>
                )}
              </div>

              <div className="section">
                <label htmlFor="email">Send Summary via Email:</label>
                <input
                  type="text"
                  id="email"
                  placeholder="Enter email addresses"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <button onClick={handleSendSummary} disabled={isProcessing}>
                  {isProcessing ? 'Processing...' : 'Send Email'}
                </button>
              </div>

              <div className="section">
                <button disabled>Generate Summary for Custom Time Range (To be implemented)</button>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default TranscriptManager;
