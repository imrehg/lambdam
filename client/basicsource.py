from __future__ import division
from time import sleep
from random import gauss, shuffle
from socketIO import SocketIO
s = SocketIO('localhost', 3000)

"""
Driver module for NI USB-6259 DAQ
"""
import ctypes
import numpy
from time import sleep
wlm = ctypes.windll.wlmData # load the DLL

int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
double = ctypes.c_double
long = ctypes.c_long

# print wlm
# for i in range(1, 9):
#     freq = float64(wlm.GetFrequencyNum(int32(i), float64(0)))
#     print freq

LZERO = long(0)
DZERO = double(0)
cInstCheckForWLM = long(-1)
cInstResetCalc = long(0)
cInstReturnMode = cInstResetCalc
cInstNotification = long(1)
cInstCopyPattern = long(2)
cInstCopyAnalysis = cInstCopyPattern
cInstControlWLM = long(3)
cInstControlDelay = long(4)
cInstControlPriority = long(5)


# # print wlm.Instantiate(cInstResetCalc, LZERO, LZERO, LZERO)
# print wlm.Instantiate(cInstReturnMode, long(0), LZERO, LZERO)

getfreq = wlm.GetFrequency
getfreq.restype = double

while True:
    try:
        freq = getfreq(DZERO)
        out = {"wavelength" : { "channel": 3, "value": freq}}
        print out
        s.emit('message', out)
        # sleep(0.001)
    except (KeyboardInterrupt):
        print("Stopping")
        break
