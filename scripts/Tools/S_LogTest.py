import sys
import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.util.logsvrclient as lclib

oLogger = lclib.LogSvrClient(None, 'localhost', 2423, 'transaction')

def RunTest(config, parameters, returnpacket):
  status = returnpacket.CreateValues(["Is_Error", 0], ["Error_Message", ""])

  for i in range(200):
    oLogger.writeLog('Tes Log %d' % i)
  