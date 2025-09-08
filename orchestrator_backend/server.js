const express = require('express');
const { initializeDatabase } = require('./db/database.js');
const Guardian = require('./services/Guardian.js');
const MissionConductor = require('./services/MissionConductor.js');

const app = express();
app.use(express.json());
const PORT = 8080;

initializeDatabase().then(db => {
    MissionConductor.setDb(db);

    // --- API Endpoint for Agents ---
    app.post('/api/agents', async (req, res) => {
        console.log('Received POST request on /api/agents');
        try {
            const { name, purpose, runtime, command } = req.body;
            const result = await db.run('INSERT INTO agents (name, purpose, runtime, command) VALUES (?, ?, ?, ?)', [name, purpose, runtime, command]);
            console.log(`Successfully created agent with ID: ${result.lastID}`);
            res.status(201).json({ id: result.lastID });
        } catch (error) {
            console.error('Error in /api/agents:', error);
            res.status(500).json({ error: 'Failed to create agent.' });
        }
    });

    // --- API Endpoint for Missions ---
    app.post('/api/missions/create', async (req, res) => {
        console.log('Received POST request on /api/missions/create');
        try {
            const { name, tasks } = req.body;
            
            console.log(`Performing ethical review for mission: ${name}`);
            const review = await Guardian.ethicalReview(name);
            if (!review.isApproved) {
                console.warn(`Ethical review FAILED for mission: ${name}. Reason: ${review.reason}`);
                return res.status(403).json(review);
            }
            console.log('Ethical review PASSED.');

            const missionResult = await db.run('INSERT INTO missions (name, status) VALUES (?, ?)', [name, 'pending']);
            const missionId = missionResult.lastID;

            for (const task of tasks) {
                await db.run('INSERT INTO mission_tasks (mission_id, agent_id, step_number, input_data, status) VALUES (?, ?, ?, ?, ?)', [missionId, task.agent_id, task.step_number, task.input_data || null, 'pending']);
            }

            console.log(`Mission ${missionId} created. Dispatching to MissionConductor...`);
            MissionConductor.executeMission(missionId);

            res.status(201).json({ id: missionId });
        } catch (error) {
            console.error('Error in /api/missions/create:', error);
            res.status(500).json({ error: 'Failed to create mission.' });
        }
    });

    app.listen(PORT, () => console.log(`MISO Factory Final Version (v31.1) is online on port ${PORT}`));

}).catch(err => {
    console.error("Server start failed:", err);
    process.exit(1);
});
