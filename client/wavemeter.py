import multiprocessing as mp
import threading
from time import sleep, time
import asyncore, socket
import random
import asyncore, socket

from time import sleep
from random import gauss, shuffle
from socketIO import SocketIO

try:
    import simplejson as json
except(ImportError):
    import json

settingsQ = mp.Queue()
readingsQ = mp.Queue()

class RemoteClient(asyncore.dispatcher):

    def __init__(self, host, path, rQ, sQ):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mysocket = SocketIO('localhost', 5000)
        self.rQ = rQ
        self.sQ = sQ

    def handle_connect(self):
        pass

    def handle_close(self):
        print "Close?"
        pass

    def readable(self):
        return True

    def handle_read(self):
        # print "Reading"
        # print "Reading", 
        # self.mysocket.emit('message', self.rQ.get())
        # self.serial = 0
        try:
            data = self.mysocket.recv()
            try:
                splits = data.split(":")
                idnum = int(splits[0])
                if idnum == 5:
                    try:
                        realdata = json.loads(":".join(splits[3:]))
                        print "Realdata", realdata
                        if realdata['name'] == 'settings':
                            self.sQ.put({'channels' : realdata['args'][0]})
                    except:
                        raise
            except:
                raise
            # if data['settings']:
            #     print data['settings']
        except(socket.timeout):
            pass

    def writable(self):
        # return True
        return not self.rQ.empty()

    def handle_write(self):
        while not self.rQ.empty():
            self.mysocket.emit('message', self.rQ.get())
        # writ = random.random() < 0.01
        # if writ:
        # print "New setting"
        # self.sQ.put({'num': random.randint(1, 11)})
        # # self.rQ.put({'set': self.serial})
        # # self.serial += 1
        # print "Written"
        pass

class Wavemeter(threading.Thread):

    daemon = True

    def __init__(self, interval, sQ, rQ, *args, **kw):
        super(Wavemeter, self).__init__()
        self.interval = interval
        self.sQ = sQ
        self.rQ = rQ
        # self.settings = {'channels' : [{'num': 1, 't': 0.01}]}
        self.settings = {'channels' : []}
        self.done = threading.Event()
        self.numchn = 16+1
        self.vals = [350.0 for i in range(self.numchn)]

    def close(self):
        self.done.set()

    def run(self):
        while not self.done.is_set():
            now = time()
            if not self.sQ.empty():
                self.settings = self.sQ.get()
            print self.settings
            for ch in self.settings['channels']:
                i = int(ch['num'])
                t = float(ch['t'])
                # do setup
                sleep(t) # wait
                # read value
                self.vals[i] += random.gauss(0, 0.1)
                timestamp = time()
                self.rQ.put({"wavelength" : { "channel": i, "value": self.vals[i], "timestamp": timestamp}})
            self.done.wait(self.interval)
            print time()-now
        
client = RemoteClient('www.python.org', '/', readingsQ, settingsQ)
# daemon = True
# thr = threading.Thread(target=asyncore.loop, kwargs={"timeout": 0.01})
# thr.start() # will run "foo"
# asyncore.loop(timeout=0.01)
wavemeterThread = Wavemeter(0.001, settingsQ, readingsQ)
wavemeterThread.start()

while True:
    try:
        asyncore.poll(timeout=0.001)
    except (KeyboardInterrupt):
        client.close()
        wavemeterThread.close()
        print "Done"
        break


