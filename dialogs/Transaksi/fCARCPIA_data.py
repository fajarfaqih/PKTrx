import com.ihsan.foundation.pobjecthelper as phelper
import sys
import simplejson


def FormSetDataEx(uideflist, params) :
  config = uideflist.config
  helper = phelper.PObjectHelper(config)

  if params.GetDatasetByName('trparam') != None :
    oForm = helper.CreateObject('FormTransaksi')
    st = oForm.SetDataEx(uideflist,params)

    return st

  Now = config.Now()
  rec = uideflist.uipData.Dataset.AddRecord()
  rec.Inputer = str(config.SecurityContext.UserId)
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.TransactionDate = int(Now)
  rec.FloatTransactionDate = int(Now)
  rec.Amount = 0.0
  rec.ReceivedFrom = rec.Inputer
  
  tahun = int(config.FormatDateTime('yyyy',Now))
  oBudgetPeriod = helper.GetObjectByNames('BudgetPeriod', {'PeriodValue': tahun})
  rec.PeriodId = oBudgetPeriod.PeriodId
  
  # Set Transaction Number
  #oService = helper.LoadScript('Transaction.TransactionHelper')
  rec.TransactionNo = '<AUTOGENERATED>' #oService.GetTransactionNumber(config,'CA')
