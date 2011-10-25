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
    ID = parameter.FirstRecord.ID

    if parameter.FirstRecord.key[:5] != 'PObj:' :
      oData,Field = helper.LoadScript('GeneralModule.S_ObjectEditor').FindObj(
        config, uideflist.uipData.PClassName,
        ((ID,parameter.FirstRecord.key),), False)
      parameter.FirstRecord.key = oData.PObjConst
    rec = eval(paramMode[parameter.FirstRecord.mode])
    rec.mode = parameter.FirstRecord.mode
    rec.ID = ID
    rec.SetFieldByName(rec.ID+'ID',rec.GetFieldByName(rec.ID))
    recT = uideflist.uipTransaction.Dataset.AddRecord()
    recT.Inputer = config.SecurityContext.UserId
    recT.TransactionDate = int(config.Now())
    recT.Cara_Bayar = 'C'
    recT.BranchCode = ''
    recT.SuperUser = 1
    #recT.AccountNo = helper.LoadScript('Transaction.S_Transaction').FindDonorAccount(
    #   config, rec.GetFieldByName(rec.ID))

def FindData(config, parameter, returns):
  helper = phelper.PObjectHelper(config)

  ClassName = parameter.FirstRecord.ClassName
  ValueID = parameter.FirstRecord.ID
  Fields = eval(parameter.FirstRecord.Fields)
  ListValue = helper.LoadScript('GeneralModule.S_ObjectEditor').AccessValuesObject(
    config, ClassName, ((Fields[0],ValueID),), Fields[1])
  returns.CreateValues(['LsValue',str(ListValue)],
   ['FieldInit',()],['ValueInit'])

def SimpanData(config, parameter, returns):
  helper = phelper.PObjectHelper(config)
  KT = 'SD001'
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
