const express = require('express'); // This defines the library
const { exec } = require('child_process'); // This allows running local files
const cors = require('cors'); // This allows React to talk to this server
const path = require('path');

const app = express(); // THIS defines 'app' and fixes your error
const PORT = 5000;

app.use(cors());
app.use(express.json());

// Your Launch Logic
app.post('/api/launch', (req, res) => {
    console.log("--- Anat3D Launch Sequence Started ---");

    // 1. BLENDER CONFIGURATION
    const blenderExe = `"C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe"`;
    const modelPath = `"C:\\Users\\harin\\OneDrive\\Desktop\\heart.blend"`;

    // 2. PYTHON CONFIGURATION
    // Assumes both2.py is in C:\Anat3D\
    const pythonScriptPath = path.join(__dirname, 'both2.py');
    
    const launchBlender = `${blenderExe} ${modelPath}`;
    const launchPython = `python "${pythonScriptPath}"`;

    // Execute Blender
    exec(launchBlender, (error) => {
        if (error) console.error(`Blender Error: ${error.message}`);
    });

    // Execute Python
    exec(launchPython, (error) => {
        if (error) console.error(`Python Error: ${error.message}`);
    });

    res.json({ status: "success", message: "Anat3D Systems Initialized" });
});

app.listen(PORT, () => {
    console.log(`Backend Bridge active on http://localhost:${PORT}`);
});