
// Import and setup
var express = require('express');
var uuid = require('node-uuid');

var app = express.createServer(express.logger());
app.use(express.bodyParser());
app.use(express.static(__dirname + '/public'));

var io = require('socket.io').listen(app);

io.configure(function(){
    io.set('log level', 6);
    io.set("transports", ["websocket"]);
    // io.set("destroy upgrade", false);
});
// End import and setup


// Main page
app.get('/', function(request, response) {

  // var socket_id = uuid();
  // response.render('home.ejs', {
  //     layout: false,
  //     socket_id: socket_id
  // });
    response.redirect('/dash');

});


function messageCenter(socket, msg) {
    console.log(msg);
    if (msg['wavelength']) {
	socket.broadcast.emit('update', msg['wavelength']);
    }
};

io.sockets.on('connection', function (socket) {
    console.log("--++ Connected: ", socket['id']);
    socket.on('message', function(msg) { messageCenter(socket, msg);} );
    socket.on('disconnect', function () { });
});

// Dashboard
app.get('/dash', function(request, response) {
  var socket_id = uuid();
  response.render('dashboard.ejs', {
      layout: false,
      title: "Dashboard",
      channels: 6,
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
