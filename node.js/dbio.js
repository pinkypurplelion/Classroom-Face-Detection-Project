// This module includes custom functions and logic enabling read/write access to the database system hosted on the web server
var fs = require('fs');

var users = {};

module.exports = {
  
    getUserData: function (userID, callback) {
        readDatabase(function (err, data) {
            // console.log(data);
            var _d = data.split("\n");
            // console.log(_d);
            for (var line in _d)
            {
                // console.log(_d[line]);
                var baa = _d[line].replace("\r", "");
                var foo = baa.split(",");
                users[foo[0]] = foo[1];
            }
            // console.log(users);
            callback(users[userID]);
        });
    }
};

function readDatabase(callback)
{
    fs.readFile("database.txt", 'utf8', function (error, data) {
        if (error) return callback(error);
        callback(null, data);
    });
}