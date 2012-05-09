import multiprocessing as mp
import threading
from time import sleep, time
import asyncore, socket
import random
import asyncore, socket

from time import sleep
from random import gauss, shuffle
from socketIO import SocketIO
import logging
import os

try:
    import simplejson as json
except(ImportError):
    import json

import wmdriver

FORMAT = '%(asctime)-15s | %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('wavemeter')
logger.setLevel(logging.DEBUG)

settingsQ = mp.Queue()
readingsQ = mp.Queue()

class RemoteClient(asyncore.dispatcher):

    def __init__(self, host, path, rQ, sQ):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(('localhost', 3000))  # needs it on windows otherwise doesn't write
        self.mysocket = SocketIO('localhost', 3000)
        self.rQ = rQ
        self.sQ = sQ

    def handle_connect(self):
        logger.debug("RC connected")
        pass

    def handle_close(self):
        logger.debug("RC Closing")

    def readable(self):
        """ Check if data is readable """
        workaround = os.name in ['nt']
        reading = not workaround
        logger.debug("RC checking readable, %s", reading)
        if workaround:
            # call manually the read function, because somehow
            # on Windows this doesn't get called even if the
            # function returns True
            self.handle_read()
        return reading

    def handle_read(self):
        logger.debug("RC reading data")
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
        except(socket.timeout):
            pass

    def writable(self):
        logger.debug("RC checking writable, %s", (not self.rQ.empty()))
        return not self.rQ.empty()

    def handle_write(self):
        logger.debug("RC writing data")
        while not self.rQ.empty():
            self.mysocket.emit('message', self.rQ.get())

class Wavemeter(threading.Thread):

    daemon = True

    def __init__(self, interval, sQ, rQ, *args, **kw):
        super(Wavemeter, self).__init__()
        self.interval = interval
        self.sQ = sQ
        self.rQ = rQ
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
            # print self.settings
            for ch in self.settings['channels']:
                i = int(ch['num'])
                t1 = int(ch['t1'])
                t2 = int(ch['t2'])
                totalt = (t1 + t2 + 10) / 1000.0
                print "Totalt", totalt
                # do setup
                wmdriver.SetExposure((t1, t2))
                sleep(totalt) # wait
                self.vals[i] = wmdriver.GetFrequency()
                timestamp = time()
                self.rQ.put({"wavelength" : { "channel": i, "value": self.vals[i], "timestamp": timestamp}})
            self.done.wait(self.interval)

client = RemoteClient('www.python.org', '/', readingsQ, settingsQ)
wavemeterThread = Wavemeter(0.0, settingsQ, readingsQ)
wavemeterThread.start()

while True:
    try:
        asyncore.poll(timeout=0.0)
    except (KeyboardInterrupt):
        client.close()
        wavemeterThread.close()
        print "Done"
        break


