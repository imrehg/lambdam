
// Import and setup
var express = require('express'),
    uuid = require('node-uuid'),
    util = require('util'),
    underscore = require('underscore');

var app = express.createServer(express.logger());
app.use(express.bodyParser());
app.use(express.static(__dirname + '/public'));

var io = require('socket.io').listen(app);

function messageCenter(socket, msg) {
    console.log("MESSAGE!");
    console.log(msg);
};

// Store settings in memory as well
var wmsettings = {};
var rooms = {};
var channelNum = 16;

// Add socket ID to the room collection
function roomAdd(id, room) {
    if (!rooms[room]) {
	rooms[room] = new Array();
    }
    rooms[room].push(id);
    console.log(rooms);
}

function roomRemove(id, room) {
    if (room) {
	rooms[room] = underscore.difference(rooms[room], [id]);
    } else {
	for (room in rooms) {
	    rooms[room] = underscore.difference(rooms[room], [id]);
	}
    }
    console.log(rooms);
}

var respserv = io.of('/channels')
    .on('connection', function(socket) {
        socket.join('announce');
	socket.emit('rooms', rooms);
        console.log(util.inspect(socket.manager.rooms));
	socket.on('subscribe',
		  function(data) {
		      console.log("SUBBBBB");
		      var room = data.channel;
		      socket.join(room);
		      roomAdd(socket.id, room);
		      var sendset = wmsettings[room] || {'channel': room, 'newchannel': true};
		      socket.emit('settings', sendset);
		      socket.broadcast.emit('rooms', rooms);
		  });
	socket.on('unsubscribe',
		  function(data) {
		      console.log("UN-SUBBBBB");
		      var room = data.channel;
		      this.in(room).emit('message', "one leaving room "+room);
		      var namespace = socket.namespace.name;
		      var numlistener = socket.manager.rooms[namespace+'/'+room].length;
		      socket.leave(room);
		      roomRemove(socket.id, room);
		      // If no more listeners, remove settings
		      if (numlistener < 2) {
			  delete wmsettings[room];
			  updateSettings();
		      }
		      socket.broadcast.emit('rooms', rooms);
		  });
	socket.on('settings',
		  function(data) {
		      var num = data.num;
		      var t1 = data.t1;
		      var t2 = data.t2;
		      wmsettings[num] = data;
		      updateSettings();
		  });
	socket.on('disconnect',
		  function() {
		      roomRemove(socket.id);
		      socket.broadcast.emit('rooms', rooms);
		      for (var i = 1; i <= channelNum; i++) {
			  var namespace = socket.namespace.name;
			  if (socket.manager.roomClients[socket.id][namespace+'/'+i]) {
			      var numlistener = socket.manager.rooms[namespace+'/'+i].length;
			      if (numlistener < 2) {
				  delete wmsettings[i];
				  updateSettings();
			      }
			  }
		      }
		  });
    });

io.configure(function(){
    io.set('log level', 6);
    io.set("transports", ["websocket"]);
});

var mainsocket = io.on('connection', function(socket) {
    socket.on('message', function(data) {
	console.log(data);
	if (data.wavelength) {
	    console.log("!!!!!!!!!!!!");
	    respserv.in(data.channel).emit("message", data);
	}
    });
});

function updateSettings() {
    console.log("New settings:");
    console.log(wmsettings);
    io.sockets.emit('settings', wmsettings);
}

// Main page
app.get('/', function(request, response) {
    response.redirect('/dash');
});

// function messageCenter(socket, msg) {
//     console.log(msg);
//     if (msg['wavelength']) {
// 	socket.broadcast.emit('update', msg['wavelength']);
//     } else if (msg['settings']) {
// 	wmsettings = msg['settings'];
// 	socket.broadcast.emit('settings', wmsettings);
//     }
// };

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
      channels: channelNum,
      socket_id: socket_id
  });
});

app.get('/chn1', function(req, res) {
    respserv.in('1').send("Some visit");
    res.send("OK");
});

// // Missing page: 404
// app.get('*', function(request, response) {
//   response.render('404.ejs', {
//       layout: false,
//       title: "Something went wrong"
//   });
// });

// Start the app
var port = process.env.PORT || 3000;
app.listen(port, function() {
  console.log("Listening on " + port);
});
