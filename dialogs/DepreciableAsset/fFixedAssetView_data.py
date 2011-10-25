import com.ihsan.foundation.pobjecthelper as phelper
import sys,os
import com.ihsan.timeutils as timeutils

def FormSetDataEx(uideflist, parameter):
  config = uideflist.config

  if (parameter.DatasetCount == 0 or
    parameter.GetDataset(0).Structure.StructureName != 'data'):
    return
    
  rec = parameter.FirstRecord

  key = 'PObj:FixedAsset#AccountNo=%s' % rec.AccountNo
  uideflist.SetData('uipFixedAsset', key)

  sOQL = "select "
  Now = config.Now()
  uipDeprHistori = uideflist.uipDepreciationHistori.Dataset
  
  sOQL = "select from AccountTransactionItem \
      [ LTransaction.TransactionCode='DEPR' and \
        AccountNo = :AccountNo \
       ] \
      ( LTransaction.ActualDate, \
        Amount, \
        self) then order by ActualDate; \
    "

  oql = config.OQLEngine.CreateOQL(sOQL)
  oql.SetParameterValueByName('AccountNo', rec.AccountNo)
  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  i = 0
  while not ds.Eof :
    oTran = uipDeprHistori.AddRecord()
    
    oTran.DeprNo = i + 1
    oTran.DeprValue = ds.Amount
    oTran.DeprDate = timeutils.AsTDateTime(config, ds.ActualDate)
    
    i+=1
    ds.Next()
  # end while
    
    
