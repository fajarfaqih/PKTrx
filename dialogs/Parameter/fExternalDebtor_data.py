import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
    config = uideflist.config
    helper = phelper.PObjectHelper(config)
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

def OnBeginProcessData (uideflist, AData) :
  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  uData = AData.uipData.GetRecord(0)
  if uData.mode == 'New' :
     pass

def SimpanData(config, parameter, returnpacket) :
    rsrc = parameter.uipData.GetRecord(0)
    #Parameter
    ObjName = 'ExternalDebtor'
    LsFieldInput = ('DebtorName','DebtorPhone','DebtorAddress','Description')
    config.BeginTransaction()
    try :
        helper = phelper.PObjectHelper(config)
        rsrc.SetFieldByName(rsrc.ID,rsrc.GetFieldByName(rsrc.ID+'ID'))
        obj = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateOrEditDataObject\
         (config, ObjName, ((rsrc.ID,rsrc.GetFieldByName(rsrc.ID)),), rsrc, LsFieldInput)
        obj.BranchCode = config.SecurityContext.GetUserInfo()[4]

        config.Commit()
    except :
        config.Rollback()
        raise
    return 1
