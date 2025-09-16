import React, { useState } from 'react';
import Login from './components/Login.jsx';
import Dashboard from './components/Dashboard.jsx';
import './index.css';
const App = () => {
  const [token, setToken] = useState(localStorage.getItem('miso_token'));
  if (!token) { return <Login setToken={setToken} />; }
  return <Dashboard setToken={setToken} />;
};
export default App;
