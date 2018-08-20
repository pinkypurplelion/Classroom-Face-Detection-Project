var fs = require("fs");
var path = require('path');
var handlebars = require('handlebars');



module.exports = {

    parseTemplate: function (templateName, context, callback) {
        fs.readFile(path.join("templates", templateName + ".html"), "utf8", function (error, data) {
            if (error) return callback(error);
            compile_template(data, context, callback);
        });
    },
};

function compile_template(template, context, callback){
    var compiled = handlebars.compile(template, { strict: true });
    var result = compiled(context);
    callback(result);
}
