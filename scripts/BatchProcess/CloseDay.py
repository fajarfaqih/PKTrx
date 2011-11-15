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
  
  #--- check transaction authorization
  sqlCheck = " \
     select count(*) \
     from transaction \
     where actualdate <= %s \
        and authstatus='F' " % (config.FormatDateTimeForQuery(ProcessDate))
  
  resSQL = config.CreateSQL(sqlCheck).rawresult
  
  # Get Last Close Day
  res = App.rexecscript('accounting','appinterface/AccountingDay.GetLastCloseDate',App.CreateValues())
  
  rec = res.FirstRecord
  if rec.Is_Err : raise '',rec.Err_Message
  
  if resSQL.GetFieldValueAt(0) > 0 :
    raise '',"Masih Terdapat Transaksi yang belum di otorisasi untuk tanggal %s s/d %s" % (
         config.FormatDateTime('dd mmm yyyy',rec.LastCloseDate),
         config.FormatDateTime('dd mmm yyyy',ProcessDate))
  
  
  #--- Process CloseDay    
  ph = App.CreateValues(['ProcessDate',ProcessDate])
  res = App.rexecscript('accounting','appinterface/AccountingDay.CloseDay',ph)

  rec = res.FirstRecord
  if rec.Is_Err : raise '',rec.Err_Message        
