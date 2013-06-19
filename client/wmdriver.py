"""
Driver module for HighFinesse WS7
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
dword = ctypes.c_ulong

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

# Amplitude Constants
cMin1 = long(0);
cMin2 = long(1);
cMax1 = long(2);
cMax2 = long(3);
cAvg1 = long(4);
cAvg2 = long(5);
validAmps = [cMin1, cMin2, cMax1, cMax2, cAvg1, cAvg2]

# Pattern and Analysis
cPatternDisable = long(0);
cPatternEnable = long(1);
cAnalysisDisable = cPatternDisable;
cAnalysisEnable = cPatternEnable;

cSignal1Interferometers = long(0);
cSignal1WideInterferometer = long(1);
cSignal1Grating = long(1);
cSignal2Interferometers = long(2);
cSignal2WideInterferometer = long(3);
cSignalAnalysis = long(4);

# Trigger parameters
cCtrlMeasurementContinue = long(0)
cCtrlMeasurementInterrupt = long(1)
cCtrlMeasurementTriggerPoll = long(2)
cCtrlMeasurementTriggerSuccess = long(3)

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

getwave = wlm.GetWavelength
getwave.restype = double
def GetWavelength():
    """ Get a single frequency reading """
    return getwave(DZERO)

getinterferencestats = wlm.GetAmplitudeNum
getinterferencestats.restype = long
def GetInterferenceStats(info=cMax1):
    """ Get interference pattern stats """
    if (info in validAmps):
        out = getinterferencestats(long(1), info, LZERO)
    else:
        out = None
    return out

gettemperature = wlm.GetTemperature
gettemperature.restype = double
def GetTemperature():
    """ Get current wavemeter temperature """
    return gettemperature(DZERO)

getpatternitemcount = wlm.GetPatternItemCount
getpatternitemcount.restype = long
def GetPatternItemCount(index):
    """ Get interferometer's point coint """
    return getpatternitemcount(index)

getpatternitemsize = wlm.GetPatternItemSize
getpatternitemsize.restype = long
def GetPatternItemSize(index):
    """ Get interferometer's data type size """
    return getpatternitemsize(index)

getpatterndata = wlm.GetPatternData
getpatterndata.restype = long
def GetPatternData(index, pointer):
    """ Get interferometer's data type size """
    return getpatterndata(index, pointer)

getpattern = wlm.GetPattern
getpattern.restype = long
def GetPattern(index):
    """ Get interferometer's data type size """
    return getpattern(index)

setpattern = wlm.SetPattern
setpattern.restype = long
def SetPattern(index, iEnable):
    """ Get interferometer's data type size """
    return setpattern(index, iEnable)

triggermeasurement = wlm.TriggerMeasurement
triggermeasurement.restype = long
def TriggerMeasurement(Action):
    """
    Interrupts, continues or triggers the measurement loop.

    Input parameters:
    cCtrlMeasurementContinue
    cCtrlMeasurementInterrupt
    cCtrlMeasurementTriggerPoll
    cCtrlMeasurementTriggerSuccess
    """
    return triggermeasurement(Action)

####
# Own functions
####

def EnableInterferogram():
    """
    Enable to always export the interferograms
    """
    SetPattern(cSignal1Interferometers, cPatternEnable)
    SetPattern(cSignal1WideInterferometer, cPatternEnable)

def Interferogram():
    """
    Get the interferogram from the two interferometers in our current
    model of wavemeter.
    """
    cnt = 1024
    inter1 = (ctypes.c_long*cnt)()
    pi1 = ctypes.cast(inter1, ctypes.POINTER(ctypes.c_long))

    inter2 = (ctypes.c_long*cnt)()
    pi2 = ctypes.cast(inter2, ctypes.POINTER(ctypes.c_long))

    GetPatternData(cSignal1Interferometers, pi1)
    GetPatternData(cSignal1WideInterferometer, pi2)

    inter1 = [int(i/6.5e4) for i in inter1]
    inter2 = [int(i/6.5e4) for i in inter2]

    return (inter1, inter2)
