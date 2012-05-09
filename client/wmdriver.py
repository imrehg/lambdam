"""
Driver module for HighFinesse WD7
"""
import ctypes
import numpy
wlm = ctypes.windll.wlmData # load the DLL

int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
double = ctypes.c_double
long = ctypes.c_long

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

getexposure = wlm.GetExposureNum
getexposure.restype = long
def GetExposure():
    """ Get exposure values (ms) """
    t1 = getexposure(long(1), long(1), LZERO)
    t2 = getexposure(long(1), long(2), LZERO)
    return (t1, t2)

setexposure = wlm.SetExposureNum
setexposure.restype = long
def SetExposure(t=(5, 5)):
    """ Set exposure values """
    ret1 = setexposure(long(1), long(1), long(t[0]))
    ret2 = setexposure(long(1), long(2), long(t[1]))
    return (ret1, ret2)

getfreq = wlm.GetFrequency
getfreq.restype = double
def GetFrequency():
    """ Get a single frequency reading """
    return getfreq(DZERO)
