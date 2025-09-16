import React, { useState, useEffect } from 'react';
import apiClient from '../api/apiClient';

const Dashboard = ({ setToken }) => {
  const [prompt, setPrompt] = useState('Create a python script to analyze a log file.');
  const [jobs, setJobs] = useState({});
  const [error, setError] = useState('');

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('miso_token');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await apiClient.post('/genesis/create', { prompt });
      const newJobId = response.data.job_id;
      setJobs(prevJobs => ({ ...prevJobs, [newJobId]: response.data }));
    } catch (err) {
      setError('Failed to create job.');
      console.error(err);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      Object.keys(jobs).forEach(jobId => {
        const job = jobs[jobId];
        if (job.status === 'accepted' || job.status === 'in_progress') {
          apiClient.get(`/genesis/status/${jobId}`)
            .then(response => {
              setJobs(prev => ({ ...prev, [jobId]: response.data }));
            })
            .catch(err => {
              console.error(`Failed to get status for job ${jobId}`, err);
            });
        }
      });
    }, 5000);
    return () => clearInterval(interval);
  }, [jobs]);

  return (
    <div>
      <h2>MISO Mission Control</h2>
      <button onClick={handleLogout} style={{ float: 'right' }}>Logout</button>
      <form onSubmit={handleSubmit}>
        <h3>Create New Project</h3>
        <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows='3' cols='60'></textarea>
        <br />
        <button type='submit'>🚀 Launch Genesis Pipeline</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <hr />
      <h3>Active Jobs</h3>
      {Object.keys(jobs).length === 0 ? <p>No jobs created yet.</p> : (
        <ul>
          {Object.entries(jobs).map(([jobId, jobDetails]) => (
            <li key={jobId}>
              <strong>Job ID:</strong> {jobId} | <strong>Status:</strong> {jobDetails.status} | <strong>Message:</strong> {jobDetails.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Dashboard;