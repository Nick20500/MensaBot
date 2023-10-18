const { readFile } = require('fs').promises;
const express = require('express');
const { request } = require('http');
const app = express();
app.listen(process.env.PORT || 3000, () => console.log("Up and running at http://localhost:3000"))

app.get('/', async (request, response) => {
    response.send( await readFile('./home.html', 'utf-8'));
});