const { readFile } = require('fs').promises;
const express = require('express');
const { request } = require('http');
const app = express();
app.listen(8080, () => console.log("Up and running"))

app.get('/', async (request, response) => {
    response.send( await readFile('./home.html', 'utf-8'));
});