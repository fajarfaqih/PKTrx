# L_TestScript.py
# script untuk test runtime POD

import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.util.logsvrclient as lclib
import sys

# globals
gid = -1
oLogger = lclib.LogSvrClient(None, 'localhost', 2423, 'dafapp')

def DoProcess(config, App, Params) :
  ProcessDate = Params.FirstRecord.param_date
    
  ph = App.CreateValues(['ProcessDate',ProcessDate])
  res = App.rexecscript('accounting','appinterface/AccountingDay.BackDate',ph)

  rec = res.FirstRecord
  if rec.Is_Err : raise '',rec.Err_Message  

def DAFScriptMain(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],    
  )

  helper = phelper.PObjectHelper(config)
  
  try:
    DoProcess(config,config.AppObject,params)
  except:
    status.Is_Err =1
    status.Err_Message = str(sys.exc_info()[1])
  # end try except  

  return 1        
