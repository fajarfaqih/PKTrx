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
  # Get Last Close Day
  res = App.rexecscript('accounting','appinterface/AccountingDay.GetLastCloseDate',App.CreateValues())
  
  rec = res.FirstRecord
  if rec.Is_Err : raise '',rec.Err_Message

  #--- check transaction authorization
  sqlCheck = " \
     select count(*) \
     from transaction \
     where actualdate <= %s \
        and authstatus='F' \
        and transactioncode <> 'TB' " % (config.FormatDateTimeForQuery(ProcessDate))
  
  resSQL = config.CreateSQL(sqlCheck).rawresult
  
  if resSQL.GetFieldValueAt(0) > 0 :
    sqlCheckBranch = " \
     select b.branchname, count(*) as TotalTrans \
     from transaction a, branch b \
     where a.branchcode = b.branchcode \
        and a.actualdate <= %s \
        and a.authstatus='F' \
        and a.transactioncode <> 'TB' \
      group by b.branchname " % (config.FormatDateTimeForQuery(ProcessDate))
    
    resSQLBranch = config.CreateSQL(sqlCheckBranch).rawresult

    LsBranch = []
    resSQLBranch.First()

    while not resSQLBranch.Eof :
      if resSQLBranch.TotalTrans > 0 :
        LsBranch.append(resSQLBranch.BranchName)
      
      resSQLBranch.Next()
    # end while

    BeginProcessdate = int(rec.LastCloseDate) + 1

    if BeginProcessdate == ProcessDate :
      strDateRange = config.FormatDateTime('dd mmm yyyy',ProcessDate)
    else :
      strDateRange = "%s s/d %s" % (
         config.FormatDateTime('dd mmm yyyy', BeginProcessdate),
        config.FormatDateTime('dd mmm yyyy', ProcessDate))

    raise '',"Masih Terdapat Transaksi yang belum di otorisasi untuk tanggal %s di cabang %s" % (
         strDateRange, ", ".join(LsBranch))
  
  
  #--- Process CloseDay    
  ph = App.CreateValues(['ProcessDate',ProcessDate])
  res = App.rexecscript('accounting','appinterface/AccountingDay.CloseDay',ph)

  rec = res.FirstRecord
  if rec.Is_Err : raise '',rec.Err_Message
