# L_TestScript.py
# script untuk test runtime POD

import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.util.logsvrclient as lclib

# globals
gid = -1
oLogger = lclib.LogSvrClient(None, 'localhost', 2423, 'dafapp')

def DAFLongScriptMain(config, parameter, pid, monfilename):
    global gid, oLogger
    
    gid = pid
    helper = phelper.PObjectHelper(config)    
    oLogger.writeLog('Proses test mulai...')
    ProsesTest(helper)
    oLogger.writeLog('Proses test selesai!')
  
    return 1

def ProsesTest(helper):
    import time, random
    global gid, oLogger
    
    #params = bp.params
    #nr = params.RecordCount
    nr = 5
    for i in range(nr):
        #rec = params.GetRecord(i)
        #pname = rec.parameter_name
        #sval  = rec.param_strval or 'N/A'
        #ival  = rec.param_intval or -999
        
        n = random.randint(1,10)
        oLogger.writeLog('pid:%d. sleeping in %d seconds...' % (gid, n))
        time.sleep(n)
        
        #if n % 3 == 0:
        #    raise 'ProsesTest', 'random error'
                