// The main server file handling all requests for the public facing web server

const express = require('express');
const next = require('next');

const dev = process.env.NODE_ENV !== 'production';
const app = next({ dev });
const handle = app.getRequestHandler();

app.prepare()
    .then(() => {
        const server = express();

        server.get('/p/:id', (req, res) => {
            const actualPage = '/post'
            const queryParams = { id: req.params.id }
            app.render(req, res, actualPage, queryParams)
        })

        server.get('*', (req, res) => {
            return handle(req, res)
        });

        server.listen(3000, (err) => {
            if (err) throw err;
            console.log('> Ready on http://localhost:3000')
        })
    })
    .catch((ex) => {
        console.error(ex.stack);
        process.exit(1)
    });

// var app = express();
// var server = require('http').Server(app);
// var io = require('socket.io')(server);
// var bodyParser = require('body-parser');
// var dbio = require('./dbio');
// var template_helper = require('./template_helper');


//
// server.listen(3000);
// console.log("Sever listening on port 3000 (192.168.0.55:3000)");
//
//
// app.use(bodyParser.json()); // support json encoded bodies
// app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies
// app.use(express.static(__dirname + '/static'));
//
//
// app.get('/messages', function (req, res) {
//     res.sendFile(__dirname + '/index.html');
// });
//
// io.on('connection', function (socket) {
//     socket.on('chat message', function(msg){
//         io.emit('chat message', msg);
//     });
// });
//
// app.get('/', function (req, res) {
//     dbio.getUserData("52376f94-5e9f-48c3-852c-a59f43a898ac", function (_user) {
//         //res.render('index', { users: _user});
//         console.log("User: " + _user);
//         var user = _user;
//
//         template_helper.parseTemplate("index", {user: _user, body: "BODY"}, function (data) {
//             res.writeHeader(200, {"Content-Type": "text/html"});
//             res.write(data);
//             res.end();
//         });
//     });
//
// });
//
// app.get('/test', function (req, res) {
//     res.render('index', { title: 'Hey', message: 'Hello there!' })
// });
//
// app.post('/', function (req, res) {
//     res.send('Got a POST request');
//     console.log("Received POST Request");
//     console.log(req.body);
//     console.log(req.body.user, req.body.userID, req.body.faceAttributes, req.body.smile);
//     user = req.body.user;
//     io.emit('chat message', user);
// });
//
//
// //POST request listener for when a new user needs to be added to the database
// app.post('/new_user', function (req, res) {
//
// });
//
// //POST request listener for when an existing user has been located from the database
// app.post('/detect_user', function (req, res) {
//
// });
