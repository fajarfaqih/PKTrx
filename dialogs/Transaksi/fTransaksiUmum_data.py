import com.ihsan.foundation.pobjecthelper as phelper
import time, sys

def SetFromKey(helper, uideflist, parameter, rec) :
  if parameter.FirstRecord.key[:5] != 'PObj:' :
      oData,Field = helper.LoadScript('GeneralModule.S_ObjectEditor').FindObj(
        uideflist.config, uideflist.uipData.PClassName,
        ((parameter.FirstRecord.ID,parameter.FirstRecord.key),), False)
      parameter.FirstRecord.key = oData.PObjConst
  helper.LoadScript('GeneralModule.S_ObjectEditor').FillDataMode(uideflist,rec, parameter)
  return rec
  
def FormSetDataEx(uideflist, parameter) :

    config = uideflist.config
    helper = phelper.PObjectHelper(uideflist.config)
    paramMode = {
     'New':('rec','TU001'),
     'NonTunaiDebit':('SetFromKey(helper, uideflist, parameter, rec)','NTD001'),
     'NonTunaiKredit':('rec','NTC001'),
     'Edit':'helper.LoadScript(\'GeneralModule.S_ObjectEditor\').FillDataMode(uideflist,rec, parameter)',
     'View':'helper.LoadScript(\'GeneralModule.S_ObjectEditor\').FillDataMode(uideflist,rec, parameter)',
     'SENTINEL':''
    }


    rec = uideflist.uipData.Dataset.AddRecord()
    rec.mode = parameter.FirstRecord.mode
    FunctionInit, KT = paramMode[rec.mode]
    rec.ID = parameter.FirstRecord.ID
    rec = eval(FunctionInit)

    recT = uideflist.uipTransaction.Dataset.AddRecord()
    recT.Inputer = config.SecurityContext.UserId
    recT.TransactionDate = int(config.Now())
    recT.KT = KT
    recT.BranchCode = ''
    recT.SuperUser = 0
def FindData(config, parameter, returns):
  helper = phelper.PObjectHelper(config)

  ClassName = parameter.FirstRecord.ClassName
  ValueID = parameter.FirstRecord.ID
  Fields = eval(parameter.FirstRecord.Fields)

  ListValue = helper.LoadScript('GeneralModule.S_ObjectEditor').AccessValuesObject(
    config, ClassName, ((Fields[0],ValueID),), Fields[1])
  returns.CreateValues(['LsValue',str(ListValue)])

def SimpanData(config, parameter, returns):
  helper = phelper.PObjectHelper(config)
  KT = parameter.uipTransaction.GetRecord(0).KT
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
