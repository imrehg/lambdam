
// Import and setup
var express = require('express');
var uuid = require('node-uuid');

var app = express.createServer(express.logger());
app.use(express.bodyParser());

var io = require('socket.io').listen(app);

io.configure(function(){
    io.set('log level', 6);
    io.set("transports", ["websocket"]);
    // io.set("destroy upgrade", false);
});
// End import and setup


// Main page
app.get('/', function(request, response) {

  var socket_id = uuid();
  response.render('home.ejs', {
      layout: false,
      socket_id: socket_id
  });

});


function messageCenter(socket, msg) {
    console.log("-->> Got me message: "+msg['text']);
    socket.broadcast.emit('update', {'type': 'wavelegth', 'value': msg['text']})
};

io.sockets.on('connection', function (socket) {
    console.log("--++ Connected: ", socket['id']);
    socket.on('message', function(msg) { messageCenter(socket, msg);} );
    socket.on('disconnect', function () { });
});

// // Socket connections
// var chdata = io.of('/data');
// chdata.on('connection', function (socket) {
//     console.log('---> Data connection');   
// });
// var chinput = io.of('/input').on('connection', function (socket) {
//     console.log('---> Input connection');
// }).on('message', function (msg) {
//     console.log('---> Input message');
//     messageCenter(msg);
// }).on('input', function (msg) {
//     console.log('---> Input input');
//     messageCenter(msg);
// });

// chinput.on('message', function (msg) {
//     console.log('---x InputMessage:',msg);
//     chdata.emit('update', msg);
// });
// chinput.on('datain', function (from, msg) {
//     console.log('---* Datain:',from,'saying',msg);
//     chdata.emit('update', msg);
// });
// io.sockets.on('connection', function (socket) {
//     console.log('---> Basic socket connection');   
// });
// io.sockets.on('msg', function (from, msg) {
//     console.log('---* Basic datain', from, 'saying', msg);
// });



// Start the app
var port = process.env.PORT || 3000;
app.listen(port, function() {
  console.log("Listening on " + port);
});
