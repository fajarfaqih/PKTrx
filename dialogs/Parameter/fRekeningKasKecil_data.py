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
    mode = parameter.FirstRecord.mode
    rec = uideflist.uipData.Dataset.AddRecord()
    rec = eval('helper.LoadScript(\'GeneralModule.S_ObjectEditor\').'+ \
      paramMode[mode])
    ID = parameter.FirstRecord.ID
    rec.ID = ID
    rec.mode = mode
    rec.SetFieldByName(ID+'ID',rec.GetFieldByName(ID))

    config = uideflist.config
    if mode == 'New' :
      rec.UserName = config.SecurityContext.UserID
      rec.OpeningDate = config.Now()
    
def OnBeginProcessData (uideflist, AData) :
  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  uData = AData.uipData.GetRecord(0)
  if uData.mode == 'New' :
     pass

def OnSetData(sender):
  rec = sender.ActiveRecord

  helper = phelper.PObjectHelper(sender.uideflist.config)

  PettyCash = helper.GetObjectByInstance('PettyCash', sender.ActiveInstance)

  rec.SetFieldByName('LBranch.Kode_Cabang',PettyCash.BranchCode)
  rec.SetFieldByName('LCurrency.Currency_Code',PettyCash.CurrencyCode)
  rec.SetFieldByName('LUser.Id_User',PettyCash.UserName)
  corporate = helper.CreateObject('Corporate')
  CabangInfo = corporate.GetCabangInfo(PettyCash.BranchCode)
  rec.SetFieldByName('LBranch.Nama_Cabang',CabangInfo.Nama_Cabang)


def SimpanData(config, parameter, returnpacket) :
    status = returnpacket.CreateValues(
       ['Is_Err',0],['Err_Message',''])

    
    rsrc = parameter.uipData.GetRecord(0)
    #Parameter
    ObjName = 'PettyCash'
    LsFieldInput = ('AccountName','Status','BranchCode',
      'CurrencyCode','OpeningDate','UserName','CashCode')
    config.BeginTransaction()
    try :
        helper = phelper.PObjectHelper(config)
        if rsrc.mode == 'New' :
          rsSeq = config.CreateSQL("select nextval('seq_pettycashid')").RawResult
          sequence = str(rsSeq.GetFieldValueAt(0)).zfill(4)
          rsrc.AccountNoId = 'PC.%s.%s.%s' % (rsrc.BranchCode,rsrc.CurrencyCode,sequence)

        CashCode = rsrc.CashCode or ''
        if CashCode != '':
          sSQLCheck = " \
                        select count(accountno) \
                        from cashaccount \
                        where cashcode='%s' \
                            and accountno <> '%s'" % ( CashCode,rsrc.AccountNoID)

          resSQL = config.CreateSQL(sSQLCheck).RawResult
          if (resSQL.GetFieldValueAt(0) or 0) > 0:
            raise '','Kode Kas yang diinput telah digunakan.\nSilakan ganti kode kas'

        rsrc.SetFieldByName(rsrc.ID,rsrc.GetFieldByName(rsrc.ID+'ID'))

        obj = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateOrEditDataObject\
         (config, ObjName, ((rsrc.ID,rsrc.GetFieldByName(rsrc.ID)),), rsrc, LsFieldInput,
         False, rsrc.mode =='New')

        if rsrc.mode == 'New' :
          obj.Balance = 0.0
          
        config.Commit()
    except :
        config.Rollback()
        status.Is_Err = 1
        status.Err_Message = str(sys.exc_info()[1])
        
    return 1
