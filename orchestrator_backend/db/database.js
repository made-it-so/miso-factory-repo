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
