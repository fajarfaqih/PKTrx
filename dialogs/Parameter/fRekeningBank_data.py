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

    if parameter.FirstRecord.mode == 'New' :
      AccountInterface = helper.GetObject('ParameterGlobal', 'GLIBANK').Get()
      oAccount = helper.GetObject('Account', AccountInterface)
      if oAccount.isnull: 'PERINGATAN', 'Akun %s tidak ditemukan' % AccountInterface

      rec.SetFieldByName('LGLInterface.Account_Code', AccountInterface)
      rec.SetFieldByName('LGLInterface.Account_Name', oAccount.Account_Name)
    
    parameter.FirstRecord.mode
    
    config = uideflist.config
    rec.OpeningDate = config.Now()

def OnBeginProcessData(uideflist, AData) :
  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  uData = AData.uipData.GetRecord(0)
  #raise '',uData.mode

def OnSetData(sender):
  rec = sender.ActiveRecord

  helper = phelper.PObjectHelper(sender.uideflist.config)

  BankCash = helper.GetObjectByInstance('BankCash', sender.ActiveInstance)

  rec.SetFieldByName('LBranch.Kode_Cabang',BankCash.BranchCode)

  rec.SetFieldByName('LBank.BankCode',BankCash.BankCode)
  rec.SetFieldByName('LBank.BankShortName',BankCash.BankName)
  
  # Set Nama Cabang
  corporate = helper.CreateObject('Corporate')
  CabangInfo = corporate.GetCabangInfo(BankCash.BranchCode)
  rec.SetFieldByName('LBranch.Nama_Cabang',CabangInfo.Nama_Cabang)

  # Set GL Interface
  AccountInterface = BankCash.AccountInterface
  oAccount = helper.GetObject('Account', AccountInterface)
  if oAccount.isnull: 'PERINGATAN', 'Akun %s tidak ditemukan' % AccountInterface

  rec.SetFieldByName('LGLInterface.Account_Code', AccountInterface)
  rec.SetFieldByName('LGLInterface.Account_Name', oAccount.Account_Name)
  
  # Set Currency
  CurrencyCode = BankCash.CurrencyCode
  oCurrency = helper.GetObject('Currency',CurrencyCode)
  if oCurrency.isnull : 'PERINGATAN', 'Kode Valuta %s tidak ditemukan' % CurrencyCode

  rec.SetFieldByName('LCurrency.Currency_Code', CurrencyCode)
  rec.SetFieldByName('LCurrency.Full_Name', oCurrency.Full_Name)


def SimpanData(config, parameter, returnpacket) :
    status = returnpacket.CreateValues(
       ['Is_Err',0],['Err_Message',''])

    if parameter.uipData.RecordCount <= 0 : return
    
    rsrc = parameter.uipData.GetRecord(0)
    #Parameter
    ObjName = 'BankCash'
    LsFieldInput = ('AccountName','Status','BranchCode','BankCode','BankName',
      'CurrencyCode','OpeningDate','BankAccountNo', 'AccountInterface','CashCode')
    config.BeginTransaction()
    try :
        helper = phelper.PObjectHelper(config)
        
        if rsrc.mode == 'New' :
          #rsSeq = config.CreateSQL("select nextval('seq_bankcashid')").RawResult
          #sequence = str(rsSeq.GetFieldValueAt(0)).zfill(8)
          #accountnumber='BankAccountNo'
          rsrc.AccountNoId = 'BA.%s.%s' % (rsrc.BankCode,rsrc.BankAccountNo)

        CashCode = rsrc.CashCode or ''
        if CashCode != '':
          CashAccount = helper.GetObjectByNames('CashAccount',{'CashCode':CashCode})
          if ( (not CashAccount.isnull and rsrc.mode == 'New') or
               (not CashAccount.isnull and rsrc.mode == 'Edit' and CashAccount.AccountNo != rsrc.AccountNoID )) :
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
