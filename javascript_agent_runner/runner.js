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
