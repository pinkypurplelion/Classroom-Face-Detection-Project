var express = require('express');
var app = express();
var server = require('http').Server(app);
var io = require('socket.io')(server);
var bodyParser = require('body-parser');

server.listen(3000);

var user = "";


app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies
app.set('view engine', 'pug');


app.get('/messages', function (req, res) {
    res.sendFile(__dirname + '/index.html');
});

io.on('connection', function (socket) {
    socket.on('chat message', function(msg){
        io.emit('chat message', msg);
    });
});

app.get('/', function (req, res) {
    res.render('index', { users: user});
});

app.get('/test', function (req, res) {
    res.render('index', { title: 'Hey', message: 'Hello there!' })
});

app.post('/', function (req, res) {
    res.send('Got a POST request');
    console.log("Received POST Request");
    console.log(req.body.user);
    user = req.body.user;
    io.emit('chat message', user);
});


//POST request listener for when a new user needs to be added to the database
app.post('/new_user', function (req, res) {

});

//POST request listener for when an existing user has been located from the database
app.post('/detect_user', function (req, res) {

});
