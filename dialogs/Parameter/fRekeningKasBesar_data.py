import com.ihsan.foundation.pobjecthelper as phelper

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

    config = uideflist.config
    rec.UserName = config.SecurityContext.UserID
    rec.OpeningDate = config.Now()
    
def OnBeginProcessData (uideflist, AData) :
  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  uData = AData.uipData.GetRecord(0)
  if uData.mode == 'New' :
     pass

def SimpanData(config, parameter, returnpacket) :
    rsrc = parameter.uipData.GetRecord(0)
    #Parameter
    ObjName = 'BranchCash'
    LsFieldInput = ('AccountName','Status','BranchCode',
      'CurrencyCode','OpeningDate')
    config.BeginTransaction()
    try :
        helper = phelper.PObjectHelper(config)
        rsrc.SetFieldByName(rsrc.ID,rsrc.GetFieldByName(rsrc.ID+'ID'))
        
        CashCode = rsrc.CashCode or ''
        if CashCode != '':
          CashAccount = helper.GetObjectByNames('CashAccount',{'CashCode':CashCode})
          if ( (not CashAccount.isnull and rsrc.mode == 'New') or
               (not CashAccount.isnull and rsrc.mode == 'Edit' and CashAccount.AccountNo != rsrc.AccountNoID )) :
            raise '','Kode Kas yang diinput telah digunakan.\nSilakan ganti kode kas'


        obj = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateOrEditDataObject\
         (config, ObjName, ((rsrc.ID,rsrc.GetFieldByName(rsrc.ID)),), rsrc, LsFieldInput,
         False, rsrc.mode =='New')


        if rsrc.mode == 'New' :
           obj.Balance = 0.0

        config.Commit()
    except :
        config.Rollback()
        raise
    return 1
