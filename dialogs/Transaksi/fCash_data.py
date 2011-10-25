import com.ihsan.foundation.pobjecthelper as phelper
import time, sys

def FormSetDataEx(uideflist, parameter) :

    config = uideflist.config
    helper = phelper.PObjectHelper(uideflist.config)
    paramMode = {
     'New':'helper.LoadScript(\'GeneralModule.S_ObjectEditor\').FillDataMode(uideflist,rec, parameter)',
     'Edit':'helper.LoadScript(\'GeneralModule.S_ObjectEditor\').FillDataMode(uideflist,rec, parameter)',
     'View':'helper.LoadScript(\'GeneralModule.S_ObjectEditor\').FillDataMode(uideflist,rec, parameter)',
     'SENTINEL':''
    }

    rec = uideflist.uipData.Dataset.AddRecord()
    rec.mode = parameter.FirstRecord.mode

    recT = uideflist.uipTransaction.Dataset.AddRecord()
    recT.Inputer = config.SecurityContext.UserId
    recT.TransactionDate = int(config.Now())
    recT.Cara_Bayar = 'C'
    recT.BranchCode = ''
    recT.SuperUser = 1

def SimpanData(config, parameter, returns):
  helper = phelper.PObjectHelper(config)
  if parameter.uipData.GetRecord(0).mode == 'In' :
    KT = 'CI001'
  else :
    KT = 'CO001'
  config.BeginTransaction()
  try :
    oDP = helper.LoadScript('Transaction.S_Transaction').CreateTransaction(
       config,parameter, KT)

    returns.CreateValues(['FieldInit',str(('TransactionDate','Inputer'))],
     ['ValueInit',str((config.Now(),config.SecurityContext.UserId))])
    config.Commit()
  except :
    config.Rollback()
    raise
