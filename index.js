const { readFile } = require('fs').promises;
const express = require('express');
const app = express();
var path = require('path');

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', async (_request, response) => {
    response.send(await readFile('./public/html/home.html', 'utf-8'));
});

app.get('/setup', async (_request, response) => {
    response.send(await readFile('./public/html/setup.html', 'utf-8'));
});

app.listen(process.env.PORT || 3000, () => console.log("Up and running at http://localhost:3000"));
