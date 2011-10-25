KodeTransaksi = ['KK','KM']

DefaultItems = [ 'Inputer',
                 'BranchCode',
                 'TransactionDate',
                 'FloatTransactionDate',
                 'LBatch.BatchId',
                 'LBatch.BatchNo',
                 'LBatch.Description',
                 'LCashAccount.AccountNo',
                 'LCashAccount.AccountName',
                 'TransactionNo',
                 'TransactionType',
                 'ShowMode',
                 'ActualDate',
                 'Amount',
                 'Casher',
                 'FundEntity',
                 ]

class fEmployeeAR :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.fSearchEmployee = None
    self.DefaultValues = {}

  def Show(self,mode=1):
    self.uipTransaction.Edit()
    self.uipTransaction.ShowMode = mode
    self.InitValues()
    self.SaveDefaultValues()
    return self.FormContainer.Show()

  def InitValues(self):
    uipTran = self.uipTransaction
    if uipTran.ShowMode == 1 : # input mode
      uipTran.Edit()
      uipTran.FundEntity = 4
    else: # edit mode
      pass

  def ClearData(self):
    self.InitValues()
    self.uipTransaction.ClearData()

    uipTran = self.uipTransaction
    uipTran.Edit()
    for item in DefaultItems :
      uipTran.SetFieldValue(item,self.DefaultValues[item])

    self.pTransaction_LBatch.SetFocus()

  def BatchAfterLookup(self, sender, linkui):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.ActualDate = uipTran.GetFieldValue('LBatch.BatchDate')
    self.DefaultValues['LBatch.BatchId'] = uipTran.GetFieldValue('LBatch.BatchId')
    self.DefaultValues['LBatch.BatchNo'] = uipTran.GetFieldValue('LBatch.BatchNo')
    self.DefaultValues['LBatch.Description'] = uipTran.GetFieldValue('LBatch.Description')
    self.DefaultValues['ActualDate'] = uipTran.ActualDate

  def TransTypeOnChange(self,sender):
    self.DefaultValues['TransactionType'] = self.uipTransaction.GetFieldValue('TransactionType')

  def SaveDefaultValues(self):
    uipTran = self.uipTransaction
    for item in DefaultItems :
      self.DefaultValues[item] = uipTran.GetFieldValue(item)
      
  def JenisTransaksiOnChange(self,sender):
    uip = self.uipTransaction
    uip.Edit()
    uip.TransactionNo = KodeTransaksi[sender.ItemIndex] + uip.TransactionNo[2:]
    
  def EmployeeAfterLookup(self, sender, linkui):
    self.uipTransaction.EmployeeName = self.uipTransaction.GetFieldValue('LEmployee.Nama_Lengkap')

  def CashAccountAfterLookup(self, sender, linkui):
    uipTran = self.uipTransaction
    self.DefaultValues['LCashAccount.AccountNo'] = uipTran.GetFieldValue('LCashAccount.AccountNo')
    self.DefaultValues['LCashAccount.AccountName'] = uipTran.GetFieldValue('LCashAccount.AccountName')

  def SearchEmployeeClick(self,sender):
    if self.fSearchEmployee == None:
      formname = 'Transaksi/fSearchDebtor'
      form = self.app.CreateForm(formname,formname,0,None,None)
      self.fSearchEmployee = form
    else:
      form = self.fSearchEmployee
    # end if
      
    if form.ShowData():
      uipTran = self.uipTransaction
      if form.mpDebtor.ActivePageIndex == 0 :
        # External Debtor
        uipTran.EmployeeName = form.uipDebtor.DebtorName
        uipTran.EmployeeId = form.uipDebtor.DebtorId
        uipTran.DebtorType = 'X'
      else:
        # Employee
        uipTran.EmployeeName = form.uipEmployee.EmployeeName
        uipTran.EmployeeId = form.uipEmployee.EmployeeId
        uipTran.DebtorType = 'E'
      # end if
      
      
    # end if
    
  def bSimpanClick(self, sender):
    if self.SimpanData() :
      if self.uipTransaction.ShowMode == 1 :
        # insert mode
        self.ClearData()
      else:
        # edit mode
        sender.ExitAction = 1
      # end if
      
  def SimpanData(self):
    app = self.app
    if app.ConfirmDialog('Yakin simpan transaksi ?'):
      self.FormObject.CommitBuffer()
      ph = self.FormObject.GetDataPacket()

      ph = self.FormObject.CallServerMethod("SimpanData", ph)
      res = ph.FirstRecord
      if res.IsErr == 1 :
        app.ShowMessage(res.ErrMessage)
        return 0
      else:

        Message = 'Transaksi Berhasil.\nNomor Transaksi : ' + res.TransactionNo
        if res.IsErr == 2:
          Message += '\n Proses Jurnal Gagal.' + res.ErrMessage
          
        app.ShowMessage(Message)

        if app.ConfirmDialog('Apakah akan cetak kwitansi ?'):
          oPrint = app.GetClientClass('PrintLib','PrintLib')()
          #app.ShowMessage("Masukkan kertas ke printer untuk cetak kwitansi")
          oPrint.doProcessByStreamName(app,ph.packet,res.StreamName)

        return 1
    #-- if
