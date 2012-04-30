from socketIO import SocketIO
s = SocketIO('localhost', 5000)

while True:
    msg = raw_input("What message to send? ")
    if len(msg) == 0:
        break
    else:
        s.emit('message', {'text': msg})
