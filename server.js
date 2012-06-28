
// Import and setup
var express = require('express'),
    uuid = require('node-uuid'),
    util = require('util');

var app = express.createServer(express.logger());
app.use(express.bodyParser());
app.use(express.static(__dirname + '/public'));

var io = require('socket.io').listen(app);

var respserv = io.sockets
    .on('connection', function(socket) {
	// console.log(this.manager);
        // console.log("ROOOOOOOOOOOOOOOOOOM");
        socket.join('lobby');
        console.log(util.inspect(socket.manager.rooms));
	socket.json.send({back: 'to you'});
    })
    .on('message', 
	function(socket, data) {  
            console.log("MESSAGE");
            console.log(util.inspect(data));
	    socket.json.send({received: data});
	});

io.configure(function(){
    io.set('log level', 1);
    io.set("transports", ["websocket"]);
    // io.set("destroy upgrade", false);
});
// End import and setup


// Main page
app.get('/', function(request, response) {
    response.redirect('/dash');
});

// Store settings in memory as well
var wmsettings = [];

function messageCenter(socket, msg) {
    console.log(msg);
    if (msg['wavelength']) {
	socket.broadcast.emit('update', msg['wavelength']);
    } else if (msg['settings']) {
	wmsettings = msg['settings'];
	socket.broadcast.emit('settings', wmsettings);
    }
};

// io.sockets.on('connection', function (socket) {
//     console.log("--++ Connected: ", socket['id']);
//     socket.emit('settings', wmsettings);
//     socket.on('message', function(msg) { messageCenter(socket, msg);} );
//     socket.on('disconnect', function () { });
// });

// Dashboard
app.get('/dash', function(request, response) {
  var socket_id = uuid();
  response.render('dashboard.ejs', {
      layout: false,
      title: "Dashboard",
      channels: 16,
      socket_id: socket_id
  });
});

// Missing page: 404
app.get('*', function(request, response) {
  response.render('404.ejs', {
      layout: false,
      title: "Something went wrong"
  });
});

// Start the app
var port = process.env.PORT || 3000;
app.listen(port, function() {
  console.log("Listening on " + port);
});
