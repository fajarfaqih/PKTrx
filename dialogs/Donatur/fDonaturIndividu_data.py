import com.ihsan.foundation.pobjecthelper as phelper
import time, sys

def FillDataNew(uideflist, rec, parameter) :
    rec.IdentityType = 'K'
    rec.Religion = 1
    rec.MartialState = 'K'
    rec.Language = 'I'
    rec.LastFormalEducation = 4
    return rec
  
def FormSetDataEx(uideflist, parameter) :

    config = uideflist.config
    helper = phelper.PObjectHelper(uideflist.config)
    paramMode = {
     'New':'FillDataNew(uideflist,rec, parameter)',
     'Edit':'helper.LoadScript(\'GeneralModule.S_ObjectEditor\').FillDataMode(uideflist,rec, parameter)',
     'View':'helper.LoadScript(\'GeneralModule.S_ObjectEditor\').FillDataMode(uideflist,rec, parameter)',
     'SENTINEL':''
    }
    rec = uideflist.uipData.Dataset.AddRecord()
    rec = eval(paramMode[parameter.FirstRecord.mode])
    ID = parameter.FirstRecord.ID
    rec.ID = ID
    rec.mode = parameter.FirstRecord.mode
    rec.TglUbah = int(config.Now())
    rec.SetFieldByName(ID+'ID',rec.GetFieldByName(ID))

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
  sData = parameter.uipData.GetRecord(0)
  Structure = parameter.Structure.GetRecord(0)
  FieldKey, Fields = eval(Structure.Fields)
  config.BeginTransaction()
  try :
    oDP = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateOrEditDataObject(
       config,Structure.ClassName,((FieldKey,sData.GetFieldByName(sData.ID+'ID')),),sData,
         Fields, False, sData.mode =='New'
       )

    #Create DonorAccount
    oDA = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateDataFromList(
       config,'DonorAccount',
       ((sData.ID,sData.GetFieldByName(sData.ID+'ID')),
        ('AccountNo',sData.GetFieldByName(sData.ID+'ID')),
        ('AccountName',sData.DonorName),
        ('Balance',0.0),
        ('BranchCode',config.SecurityContext.GetUserInfo()[4]),
        ('CurrencyCode','000'),
        ('OpeningDate',sData.TglUbah),
        ('Status','A'))
       )

    config.Commit()
  except :
    config.Rollback()
    raise
