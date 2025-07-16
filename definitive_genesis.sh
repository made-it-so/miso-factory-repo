#!/bin/bash
set -e
# ==============================================================================
# MISO FACTORY - DEFINITIVE GENESIS SCRIPT v31.0 (FINAL)
# ==============================================================================
echo "--- [MISO Definitive Build Protocol v31.0 Initiated] ---"
# NOTE: This script is now designed to generate files locally for Git.
# It does not require an API key and does not purge a remote server.

echo "[1/2] Generating Source Directories..."
mkdir -p ./orchestrator_backend/services
mkdir -p ./orchestrator_backend/db
mkdir -p ./ui_frontend/src
mkdir -p ./python_agent_runner
mkdir -p ./javascript_agent_runner

echo "[2/2] Creating All Project Files..."

# --- docker-compose.yml (FINAL ARCHITECTURE) ---
cat << 'EODC' > docker-compose.yml
services:
  orchestrator:
    build: ./orchestrator_backend
    ports: ["8080:8080"]
    env_file: ./orchestrator_backend/backend.env
    restart: unless-stopped
  frontend:
    build: ./ui_frontend
    ports: ["80:80"]
    depends_on: [orchestrator]
    restart: unless-stopped
  python_runner:
    build: ./python_agent_runner
    restart: unless-stopped
  javascript_runner:
    build: ./javascript_agent_runner
    restart: unless-stopped
EODC

# --- Orchestrator Files ---
# Create a blank .env file; it will be populated by the deployment server.
touch orchestrator_backend/backend.env
cat << 'EOBPJ' > orchestrator_backend/package.json
{"name":"miso-orchestrator","version":"31.0.0","main":"server.js","scripts":{"start":"node server.js"},"dependencies":{"@google/generative-ai":"^0.12.0","cors":"^2.8.5","express":"^4.19.2","sqlite":"^5.1.1","sqlite3":"^5.1.7"}}
EOBPJ
cat << 'EOBDF' > orchestrator_backend/Dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
RUN npm rebuild sqlite3
COPY . .
CMD [ "node", "server.js" ]
EOBDF
cat << 'EODB' > orchestrator_backend/db/database.js
const { open } = require('sqlite');
const sqlite3 = require('sqlite3');
async function initializeDatabase() {
  const db = await open({ filename: './db/factory.sqlite', driver: sqlite3.Database });
  await db.exec('CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY, name TEXT NOT NULL, purpose TEXT, runtime TEXT, command TEXT, status TEXT DEFAULT "idle");');
  await db.exec('CREATE TABLE IF NOT EXISTS missions (id INTEGER PRIMARY KEY, name TEXT, status TEXT);');
  await db.exec('CREATE TABLE IF NOT EXISTS mission_tasks (id INTEGER PRIMARY KEY, mission_id INTEGER, agent_id INTEGER, step_number INTEGER, status TEXT, input_data TEXT, output_data TEXT);');
  return db;
}
module.exports = { initializeDatabase };
EODB
cat << 'EOBG' > orchestrator_backend/services/Guardian.js
const { GoogleGenerativeAI } = require('@google/generative-ai');
const genAI = process.env.GEMINI_API_KEY ? new GoogleGenerativeAI(process.env.GEMINI_API_KEY) : null;
module.exports = {
  ethicalReview: async (missionPurpose) => {
    if (!genAI) return { isApproved: true, justification: 'AI Core not configured. Bypassing ethical review.' };
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro-latest" });
    const prompt = 'Review the following mission description. If it violates ethical norms, respond with only "VETO". Otherwise, respond with "PROCEED".\n\nMission: "' + missionPurpose + '"';
    const result = await model.generateContent(prompt);
    const decision = result.response.text().trim().toUpperCase();
    return { isApproved: !decision.includes('VETO'), justification: decision };
  },
  genAI: genAI
};
EOBG
cat << 'EOMC' > orchestrator_backend/services/MissionConductor.js
const { genAI } = require('./Guardian.js');
let db;
module.exports = {
  setDb: (dbInstance) => { db = dbInstance; },
  executeMission: async (missionId) => {
    console.log(`[MissionConductor]: Starting execution for mission ID: ${missionId}`);
    await db.run("UPDATE missions SET status = 'running' WHERE id = ?", missionId);
    const tasks = await db.all('SELECT * FROM mission_tasks WHERE mission_id = ? ORDER BY step_number ASC', missionId);
    let currentInput = '';
    try {
      for (const task of tasks) {
        console.log(`[MissionConductor]: Executing step ${task.step_number} with agent ${task.agent_id}...`);
        const agent = await db.get('SELECT * FROM agents WHERE id = ?', task.agent_id);
        if (!agent) throw new Error(`Agent with ID ${task.agent_id} not found.`);
        const effectiveInput = (task.input_data ? task.input_data + '\\n' : '') + currentInput;
        await db.run("UPDATE mission_tasks SET status = 'running', input_data = ? WHERE id = ?", [effectiveInput, task.id]);
        let output = '';
        if (agent.runtime === 'MISO_AI') {
          console.log('[MissionConductor]: Calling MISO AI Core directly...');
          const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro-latest" });
          const result = await model.generateContent(effectiveInput);
          output = result.response.text();
        } else {
          console.log(`[MissionConductor]: Routing to ${agent.runtime}...`);
          const response = await fetch(`http://${agent.runtime}:8000/execute`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ command: agent.command, input: effectiveInput })
          });
          if (!response.ok) throw new Error(`Agent runner ${agent.runtime} failed with status ${response.status}`);
          const resJson = await response.json();
          output = resJson.output;
        }
        await db.run("UPDATE mission_tasks SET status = 'complete', output_data = ? WHERE id = ?", [output, task.id]);
        currentInput = output;
      }
      await db.run("UPDATE missions SET status = 'complete' WHERE id = ?", missionId);
      console.log(`[MissionConductor]: Mission ${missionId} completed successfully.`);
      console.log(`[MissionConductor]: FINAL MISSION OUTPUT:\n---BEGIN---\n${currentInput}\n----END----`);
    } catch (error) {
      await db.run("UPDATE missions SET status = 'error' WHERE id = ?", missionId);
      console.error(`[MissionConductor]: Mission failed. Last error: ${error.message}`);
    }
  }
};
EOMC
cat << 'EOS' > orchestrator_backend/server.js
const express = require('express');
const { initializeDatabase } = require('./db/database.js');
const Guardian = require('./services/Guardian.js');
const MissionConductor = require('./services/MissionConductor.js');
const app = express();
app.use(express.json());
const PORT = 8080;
initializeDatabase().then(db => {
    MissionConductor.setDb(db);
    app.post('/api/agents', async (req, res) => {
        const { name, purpose, runtime, command } = req.body;
        const result = await db.run('INSERT INTO agents (name, purpose, runtime, command) VALUES (?, ?, ?, ?)', [name, purpose, runtime, command]);
        res.status(201).json({ id: result.lastID });
    });
    app.post('/api/missions/create', async (req, res) => {
        const { name, tasks } = req.body;
        const review = await Guardian.ethicalReview(name);
        if (!review.isApproved) return res.status(403).json(review);
        const missionResult = await db.run('INSERT INTO missions (name, status) VALUES (?, ?)', [name, 'pending']);
        const missionId = missionResult.lastID;
        for (const task of tasks) {
            await db.run('INSERT INTO mission_tasks (mission_id, agent_id, step_number, input_data, status) VALUES (?, ?, ?, ?, ?)', [missionId, task.agent_id, task.step_number, task.input_data || null, 'pending']);
        }
        MissionConductor.executeMission(missionId);
        res.status(201).json({ id: missionId });
    });
    app.listen(PORT, () => console.log(`MISO Factory Final Version (v31.0) is online on port ${PORT}`));
}).catch(err => { console.error("Server start failed:", err); process.exit(1); });
EOS

# --- Python Agent Runner ---
cat << 'EOPRF' > python_agent_runner/Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install flask
COPY . .
CMD ["python", "runner.py"]
EOPRF
cat << 'EOPRP' > python_agent_runner/runner.py
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    command = data.get('command')
    input_data = data.get('input', '')
    
    try:
        result = subprocess.run(
            command,
            input=input_data,
            text=True,
            capture_output=True,
            shell=True,
            check=True
        )
        return jsonify({'output': result.stdout.strip()})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.stderr.strip()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOPRP

# --- JavaScript Agent Runner ---
cat << 'EOJRF' > javascript_agent_runner/Dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["node", "runner.js"]
EOJRF
cat << 'EOJSP' > javascript_agent_runner/package.json
{"name":"js-runner","version":"1.0.0","main":"runner.js","scripts":{"start":"node runner.js"},"dependencies":{"express":"^4.19.2"}}
EOJSP
cat << 'EOJSR' > javascript_agent_runner/runner.js
const express = require('express');
const { exec } = require('child_process');
const app = express();
app.use(express.json());

app.post('/execute', (req, res) => {
    const { command, input } = req.body;
    const proc = exec(command, (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({ error: stderr.trim() });
        }
        res.json({ output: stdout.trim() });
    });
    if (input) {
        proc.stdin.write(input);
        proc.stdin.end();
    }
});

app.listen(8000, () => console.log('JavaScript Agent Runner is online.'));
EOJSR

# --- UI Files ---
cat << 'EOUIF' > ui_frontend/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
RUN echo 'server { listen 80; root /usr/share/nginx/html; index index.html; location / { try_files $uri $uri/ /index.html; } location /api/ { proxy_pass http://orchestrator:8080; } }' > /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]
EOUIF
cat << 'EOUIP' > ui_frontend/package.json
{"name":"ui-frontend","version":"1.0.0","type":"module","scripts":{"build":"vite build"},"dependencies":{"react":"^18.2.0","react-dom":"^18.2.0"},"devDependencies":{"@vitejs/plugin-react":"^4.2.1","vite":"^5.2.0"}}
EOUIP
cat << 'EOUIH' > ui_frontend/index.html
<!doctype html><html lang="en"><head><meta charset="UTF-8" /><title>MISO Factory</title></head><body><div id="root"></div><script type="module" src="/src/main.jsx"></script></body></html>
EOUIH
cat << 'EOUIM' > ui_frontend/src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
ReactDOM.createRoot(document.getElementById('root')).render(React.createElement('h1', null, 'MISO Factory - v31.0 Online'));
EOUIM