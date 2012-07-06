import multiprocessing as mp
import threading
from time import sleep, time
import asyncore, socket
import random
import asyncore, socket

from time import sleep
from socketIO import SocketIO, websocket
import logging
import os
import serial

try:
    import simplejson as json
except(ImportError):
    import json

dummy = True
if not dummy:
    import wmdriver
else:
    from random import gauss


FORMAT = '%(asctime)-15s | %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('wavemeter')
logger.setLevel(logging.INFO)

settingsQ = mp.Queue()
readingsQ = mp.Queue()

port = int(os.environ['PORT']) if os.environ['PORT'] else 5000

class Switcher(object):

    def __init__(self, port):
        self.ser = serial.Serial(port,
                                 115200,
                                 timeout=1,
                                 parity=serial.PARITY_NONE,
                                 bytesize=8,
                                 stopbits=1,
                                 xonxoff=1)
        self.terminator = ""

    def setChannel(self, i):
        self.ser.write("%d%s" %(i, self.terminator))

class RemoteClient(asyncore.dispatcher):

    def __init__(self, host, path, rQ, sQ, switch):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(('localhost', port))  # needs it on windows otherwise doesn't write
        self.mysocket = SocketIO('localhost', port)
        self.rQ = rQ
        self.sQ = sQ
        self.switch = switch

    def handle_connect(self):
        logger.debug("RC connected")
        pass

    def handle_close(self):
        logger.debug("RC Closing")

    def readable(self):
        """ Check if data is readable """
        workaround = True
        # workaround = os.name in ['nt']
        reading = not workaround
        # logger.debug("RC checking readable, %s", reading)
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
                            channels = []
                            for k in realdata['args'][0]:
                                channels += [(realdata['args'][0][k])]
                            self.sQ.put({'channels' : channels})
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
            for ch in self.settings['channels']:
                i = int(ch['num'])
                t1 = int(ch['t1'])
                t2 = int(ch['t2'])
                # have to add some extra delay of there are switching involved
                # especially if there's a big difference in the exposure times
                # the optimal value depends on: number of channels, current and
                # previous channel exposure time, and probably other things
                tdelay = 50  # ms
                totalt = (t1 + t2 + tdelay) / 1000.0  
                if not dummy:
                    wmdriver.SetExposure((t1, t2))
                    switch.setChannel(i-1)  # Channel number goes from 0  
                    xt1, xt2 = wmdriver.GetExposure()
                    logger.info("Setting: %d / %d || %d / %d" %(t1, xt1, t2, xt2))
                    if (t1 != xt1) | (t2 != xt2):
                        logger.info("Exposure setting failed? %d / %d || %d / %d" %(t1, xt1, t2, xt2))
                    sleep(totalt) # wait
                    self.vals[i] = wmdriver.GetWavelength()
                else:
                    sleep(totalt)
                    self.vals[i] += gauss(0, 0.01)
                logger.debug("Channel %d: measured %f" %(i, self.vals[i]))
                timestamp = time()
                self.rQ.put({"wavelength" : { "channel": i, "value": self.vals[i], "timestamp": timestamp}})
            self.done.wait(self.interval)

if not dummy:
    switch = Switcher("COM3")
else:
    switch = None
client = RemoteClient('www.python.org', '/', readingsQ, settingsQ, switch)
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
    except (websocket.WebSocketException):
        raise
        print "Broken connection"
        break
    


