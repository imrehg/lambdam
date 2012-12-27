import multiprocessing as mp
import threading
from time import sleep, time
import asyncore, socket
import random
import asyncore, socket

from time import sleep, time
from socketIO import SocketIO, websocket, enableTrace
import logging
import os
import serial

try:
    import simplejson as json
except(ImportError):
    import json

dummy = False
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

try:
    port = int(os.environ['PORT'])
except KeyError,ValueError:
    port = 5000

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
        self.ser.write(chr(i))  # send binary number

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
        lastdelay = None
        lastchannel = None
        while not self.done.is_set():
            now = time()
            if not self.sQ.empty():
                self.settings = self.sQ.get()
            channels = len(self.settings['channels']);
            multichannel = (channels > 1)
            for ch in self.settings['channels']:
                i = int(ch['num'])
                t1 = int(ch['t1'])
                t2 = int(ch['t2'])
                # have to add some extra delay of there are switching involved
                # especially if there's a big difference in the exposure times
                # the optimal value depends on: number of channels, current and
                # previous channel exposure time, and probably other things
                tdelay = 10;
                if multichannel:
                    if lastdelay:
                        tdelay += lastdelay + 100
                    lastdelay = t1 + t2
                totalt = (t1 + t2 + tdelay) / 1000.0  
                if not dummy:
                    wmdriver.SetExposure((t1, 0))
                    if lastchannel <> i:
                        switch.setChannel(i-1)  # Channel number goes from 0
                        lastchannel = i
                    xt1, xt2 = wmdriver.GetExposure()
                    logger.debug("Setting: %d / %d || %d / %d" %(t1, xt1, t2, xt2))
                    if (t1 != xt1) | (t2 != xt2):
                        logger.debug("Exposure setting failed? %d / %d || %d / %d" %(t1, xt1, t2, xt2))
                    wmdriver.TriggerMeasurement(wmdriver.cCtrlMeasurementContinue)

                    # # start new measurement
                    # if multichannel:
                    #     sleep(0.005)
                    #     wmdriver.TriggerMeasurement(wmdriver.cCtrlMeasurementTriggerPoll)
                    # else:
                    #     wmdriver.TriggerMeasurement(wmdriver.cCtrlMeasurementContinue)

                    sleep(totalt) # wait
                    self.vals[i] = wmdriver.GetWavelength()
                    imax1, imax2 = wmdriver.GetInterferenceStats(wmdriver.cMax1), wmdriver.GetInterferenceStats(wmdriver.cMax2);
                    intermax = imax1 if imax1 > imax2 else imax2
                    inter1, inter2 = wmdriver.Interferogram()
                else:
                    sleep(totalt)
                    self.vals[i] += gauss(0, 0.01)
                    intermax = 1000;
                    inter1, inter2 = [0]*1024, [0]*1024
                logger.debug("Channel %d: measured %f" %(i, self.vals[i]))
                timestamp = time()
                self.rQ.put({"wavelength" : { "channel": i,
                                              "value": self.vals[i],
                                              "timestamp": timestamp,
                                              "exposureval": intermax,
                                              "inter1": inter1,
                                              "inter2": inter2,
                                              }
                             })
            # Return the temperature after one round;
            if not dummy:
                temperature = wmdriver.GetTemperature()
            else:
                temperature = 21
            self.rQ.put({"temperature" : temperature, "timestamp": time()});
            if (len(self.settings['channels']) < 1):
                sleep(0.1)
            self.done.wait(self.interval)

if not dummy:
    switch = Switcher("COM3")
    wmdriver.EnableInterferogram()
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
        print "Broken connection"
        break
    


