import sys
import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist,params):
  config = uideflist.config
  uipData = uideflist.uipData.Dataset.AddRecord()

  app = config.AppObject
  res = app.rexecscript('accounting','appinterface/AccountingDay.GetLastCloseDate',app.CreateValues())
  
  rec = res.FirstRecord
  if rec.Is_Err : raise '',rec.Err_Message

  LastCloseDate = int(rec.LastCloseDate)
  uipData.LastCloseDate = LastCloseDate
  uipData.ProcessDate = LastCloseDate
  

