import express from "express";
import ViteExpress from "vite-express";
import {readFileSync} from "fs";
import path from "path";

const app = express();

app.use(express.json());

// Catch-all route to serve the Vite app
app.get('/', (_req, res) => {
  res.sendFile(path.resolve('src', 'client', 'html', 'home.html'));
});

app.get('/setup', (_req, res) => {
    try {
        const fileContent = readFileSync('./src/client/html/setup.html', 'utf-8');
        res.send(fileContent);
    } catch (error) {
        console.error(error);
        res.status(500).send('Internal Server Error');
    }
});

app.post('/message-setup', (req, res) => {
    try {
        console.log("mensas: " + req.body.mensas + ", days: " + req.body.days + ", time: " + req.body.time);
        //TODO: store the choosen settings for the given user
        res.status(200).send();
    } catch (error) {
        res.status(500).send(error);
    }
});

app.post('/create-account', (req, res) => {
    try {
        console.log("phone number: " + req.body.phone + ", pw: " + req.body.password);
        //TODO: create & store new account
        res.status(200).send();
    } catch (error) {
        res.status(500).send(500);
    }
});

ViteExpress.listen(app, 5173, () =>
    console.log("Server is listening on http://localhost:5173"),
);
