
// Import and setup
var express = require('express'),
    uuid = require('node-uuid'),
    util = require('util');

var app = express.createServer(express.logger());
app.use(express.bodyParser());
app.use(express.static(__dirname + '/public'));

var io = require('socket.io').listen(app);

function messageCenter(socket, msg) {
    console.log("MESSAGE!");
    console.log(msg);
};


var respserv = io.of('/channels')
    .on('connection', function(socket) {
        socket.join('announce');
        console.log(util.inspect(socket.manager.rooms));
	socket.on('subscribe',
		  function(data) {
		      console.log("SUBBBBB");
		      var room = data.channel;
		      socket.join(room);
		      this.in(room).emit('message', "new arrival to "+room);
		  });
	socket.on('unsubscribe',
		  function(data) {
		      console.log("UN-SUBBBBB");
		      var room = data.channel;
		      this.in(room).emit('message', "one leaving room "+room);
		      socket.leave(room);
		  });
    });

io.configure(function(){
    io.set('log level', 6);
    io.set("transports", ["websocket"]);
});


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

app.get('/chn1', function(req, res) {
    respserv.in('1').send("Some visit");
    res.send("OK");
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
