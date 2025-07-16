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
