from simplejson import dumps
from threading import Thread, Event
from urllib import urlopen
from websocket import create_connection, enableTrace, WebSocketApp


class SocketIO(object):

    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.__do_handshake()
        self.__connect()
        self.heartbeatThread = RhythmicThread(self.heartbeatTimeout - 2, self.__send_heartbeat)
        self.heartbeatThread.start()
        self.msgid = 0

    def __do_handshake(self):
        try:
            response = urlopen('http://%s:%d/socket.io/1/' % (self.host, self.port))
        except IOError:
            raise SocketIOError('Could not start connection')
        if 200 != response.getcode():
            raise SocketIOError('Could not establish connection')
        self.sessionID, heartbeatTimeout, connectionTimeout, supportedTransports = response.readline().split(':')
        self.heartbeatTimeout = int(heartbeatTimeout)
        self.connectionTimeout = int(connectionTimeout)
        if 'websocket' not in supportedTransports.split(','):
            raise SocketIOError('Could not parse handshake')

    def __connect(self):
        self.connection = create_connection('ws://%s:%d/socket.io/1/websocket/%s' % (self.host, self.port, self.sessionID))
        print "->", self.connection.recv()
        print("ID", self.sessionID)
        # self.connection.send('1::')
        # print self.connection.recv()

        # msg = '5::/input:{"name":"message", "args": {"hell": "yeah"}}'
        # msg = '5:1:/input:{"name":"message", "args": {"hell": "no"}}'
        # print msg
        # self.connection.send(msg)
        # namespace = "input"
        # sendData = '1:%s::' %namespace
        # self.connection.send(sendData)
        # print "namespace: ", namespace, sendData
        # url = 'ws://%s:%d/socket.io/1/websocket/%s' % (self.host, self.port, self.sessionID)
        # self.connection = WebSocketApp(url, on_message=self.received)
        # self.connection.run_forever()
        # self.connection.send('1::/input')
        # print("ID", self.sessionID)

    def received(self, message):
        print("Received: ", message)

    def __del__(self):
        try:
            self.heartbeatThread.cancel()
            self.connection.close()
        except AttributeError:
            pass

    def __send_heartbeat(self):
        self.connection.send('2::')
        print "->", self.connection.recv()

    def emit(self, eventName, eventData):
        self.msgid += 1
        sentString = '5:%d::' %(self.msgid) + dumps(dict(name=eventName, args=eventData))
        print(sentString)
        self.connection.send(sentString)
        print "->", self.connection.recv()


class SocketIOError(Exception):
    pass


class RhythmicThread(Thread):
    'Execute function every few seconds'

    daemon = True

    def __init__(self, intervalInSeconds, function, *args, **kw):
        super(RhythmicThread, self).__init__()
        self.intervalInSeconds = intervalInSeconds
        self.function = function
        self.args = args
        self.kw = kw
        self.done = Event()

    def cancel(self):
        self.done.set()

    def run(self):
        self.done.wait(self.intervalInSeconds)
        while not self.done.is_set():
            self.function(*self.args, **self.kw)
            self.done.wait(self.intervalInSeconds)
