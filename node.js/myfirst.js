var express = require('express');
var app = express();
var bodyParser = require('body-parser');


app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies

app.get('/', function (req, res) {
    res.send('Hello World');
});

app.post('/', function (req, res) {
    res.send('Got a POST request');
    console.log("Received POST Request");
    console.log(req.body.user)
});

app.listen(3000, () => console.log("App is now listening on port 3000"));