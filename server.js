const express = require('express');
const { exec } = require('child_process');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

// 🔹 Blender + model paths
const blenderExe = `"C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe"`;
const heartModelPath = `"C:\\Users\\harin\\OneDrive\\Desktop\\heart.blend"`;
const brainModelPath = `"C:\\Users\\harin\\OneDrive\\Desktop\\humanbrain.blend"`;
const mouthModelPath = `"C:\\Users\\harin\\OneDrive\\Desktop\\mouth.blend"`;

// 🔹 Python script path
const pythonScriptPath = path.join(__dirname, 'both2.py');

// 🔹 IMPORTANT: exact Python that has cv2 installed
const pythonExe = `"C:\\Users\\harin\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"`;

// =============================
// Launch Blender only
// =============================
app.post('/api/launch-blender', (req, res) => {
    console.log("--- Launching Blender ---");

    const launchBlender = `${blenderExe} ${heartModelPath}`;

    exec(launchBlender, (error, stdout, stderr) => {
        if (error) {
            console.error(`Blender Error: ${error.message}`);
            console.error(stderr);
        } else {
            console.log(stdout);
        }
    });

    res.json({ status: "success", message: "Blender launching" });
});

// =============================
// Launch Python only
// =============================
app.post('/api/launch-python', (req, res) => {
    console.log("--- Launching Python ---");

    const launchPython = `${pythonExe} "${pythonScriptPath}"`;

    exec(launchPython, (error, stdout, stderr) => {
        if (error) {
            console.error(`Python Error: ${error.message}`);
            console.error(stderr);
        } else {
            console.log(stdout);
        }
    });

    res.json({ status: "success", message: "Python script launching" });
});

// =============================
// Launch BOTH (Blender + Python)
// =============================
app.post('/api/launch', (req, res) => {
    console.log("--- Anat3D Launch Sequence Started ---");

    const launchBlender = `${blenderExe} ${heartModelPath}`;
    const launchPython = `${pythonExe} "${pythonScriptPath}"`;

    exec(launchBlender, (error, stdout, stderr) => {
        if (error) {
            console.error(`Blender Error: ${error.message}`);
            console.error(stderr);
        } else {
            console.log(stdout);
        }
    });

    exec(launchPython, (error, stdout, stderr) => {
        if (error) {
            console.error(`Python Error: ${error.message}`);
            console.error(stderr);
        } else {
            console.log(stdout);
        }
    });

    res.json({ status: "success", message: "Anat3D Systems Initialized" });
});

// =============================
// Launch Brain (Blender + Python)
// =============================
app.post('/api/launch-brain', (req, res) => {
    console.log("--- Brain Launch Sequence Started ---");

    const launchBlender = `${blenderExe} ${brainModelPath}`;
    const launchPython = `${pythonExe} "${pythonScriptPath}"`;

    exec(launchBlender, (error, stdout, stderr) => {
        if (error) {
            console.error(`Blender (Brain) Error: ${error.message}`);
            console.error(stderr);
        } else {
            console.log(stdout);
        }
    });

    exec(launchPython, (error, stdout, stderr) => {
        if (error) {
            console.error(`Python (Brain) Error: ${error.message}`);
            console.error(stderr);
        } else {
            console.log(stdout);
        }
    });

    res.json({ status: "success", message: "Brain Systems Initialized" });
});

// =============================
// Launch Mouth (Blender + Python)
// =============================
app.post('/api/launch-mouth', (req, res) => {
    console.log("--- Mouth Launch Sequence Started ---");

    const launchBlender = `${blenderExe} ${mouthModelPath}`;
    const launchPython = `${pythonExe} "${pythonScriptPath}"`;

    exec(launchBlender, (error, stdout, stderr) => {
        if (error) {
            console.error(`Blender (Mouth) Error: ${error.message}`);
            console.error(stderr);
        } else {
            console.log(stdout);
        }
    });

    exec(launchPython, (error, stdout, stderr) => {
        if (error) {
            console.error(`Python (Mouth) Error: ${error.message}`);
            console.error(stderr);
        } else {
            console.log(stdout);
        }
    });

    res.json({ status: "success", message: "Mouth Systems Initialized" });
});

// =============================
app.listen(PORT, () => {
    console.log(`Backend Bridge active on http://localhost:${PORT}`);
});
