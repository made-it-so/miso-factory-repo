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
