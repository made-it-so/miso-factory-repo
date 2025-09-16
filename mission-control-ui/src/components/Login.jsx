import React, { useState } from 'react';
import apiClient from '../api/apiClient';
const Login = ({ setToken }) => {
  const [username, setUsername] = useState('miso_admin');
  const [password, setPassword] = useState('madeitso');
  const [error, setError] = useState('');
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      const response = await apiClient.post('/auth/token', formData);
      const accessToken = response.data.access_token;
      setToken(accessToken);
      localStorage.setItem('miso_token', accessToken);
    } catch (err) {
      setError('Login failed. Check username or password.');
    }
  };
  return (
    <div>
      <h2>MISO Mission Control Login</h2>
      <form onSubmit={handleSubmit}>
        <div><label>Username:</label><input type='text' value={username} onChange={(e) => setUsername(e.target.value)} /></div>
        <div><label>Password:</label><input type='password' value={password} onChange={(e) => setPassword(e.target.value)} /></div>
        <button type='submit'>Login</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};
export default Login;
