import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormSetDataEx(uideflist, parameter) :
    helper = phelper.PObjectHelper(uideflist.config)
    paramMode = {
    'New':'ClearDataMode(uideflist,rec, parameter)',
    'Edit':'FillDataMode(uideflist,rec, parameter)',
    'View':'FillDataMode(uideflist,rec, parameter)',
    'SENTINEL':''
    }
    rec = uideflist.uipData.Dataset.AddRecord()
    rec = eval('helper.LoadScript(\'GeneralModule.S_ObjectEditor\').'+ \
      paramMode[parameter.FirstRecord.mode])
    ID = parameter.FirstRecord.ID
    rec.ID = ID
    rec.mode = parameter.FirstRecord.mode
    rec.SetFieldByName(ID+'ID',rec.GetFieldByName(ID))

def BankOnSetData(sender):
  rec = sender.ActiveRecord
  helper = phelper.PObjectHelper(sender.uideflist.config)

def OnBeginProcessData (uideflist, AData) :
  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  uData = AData.uipData.GetRecord(0)
  if uData.mode == 'New' :
     pass

def SimpanData(config, parameter, returnpacket) :
    status = returnpacket.CreateValues(
       ['Is_Err',0],['Err_Message',''])

    rsrc = parameter.uipData.GetRecord(0)
    #Parameter
    ObjName = 'Bank'
    LsFieldInput = ('BankName','BankShortName')
    config.BeginTransaction()
    try :
        helper = phelper.PObjectHelper(config)
        if rsrc.mode == 'New' :
          oBank = helper.GetObject('Bank',rsrc.BankCodeId)
          
          if ( not oBank.isnull) :
            raise '','Kode Bank yang diinput telah digunakan.\nSilakan ganti Kode Bank'

        rsrc.SetFieldByName(rsrc.ID,rsrc.GetFieldByName(rsrc.ID+'ID'))
        obj = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateOrEditDataObject\
         (config, ObjName, ((rsrc.ID,rsrc.GetFieldByName(rsrc.ID)),), rsrc, LsFieldInput)

        config.Commit()
    except :
        config.Rollback()
        status.Is_Err = 1
        status.Err_Message = str(sys.exc_info()[1])

    return 1
