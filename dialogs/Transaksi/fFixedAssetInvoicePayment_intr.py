KodeTransaksi = ['KK','KM']

class fFixedAssetInvoicePayment :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.fSearchEmployee = None
    self.fSearchBudget = None

  def Show(self , mode = 1):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.ShowMode = mode
    uipTran.Amount = 0.0
    
    return self.FormContainer.Show()

  def InvoiceAfterLookup (self, sender, linkui):
    self.uipTransaction.Edit()
    self.uipTransaction.Amount = self.uipTransaction.GetFieldValue('LInvoiceFA.InvoiceAmount')
    pass

  def SearchEmployeeClick(self,sender):
    if self.fSearchEmployee == None:
      formname = 'Transaksi/fSearchEmployee'
      form = self.app.CreateForm(formname,formname,0,None,None)
      self.fSearchEmployee = form
    else:
      form = self.fSearchEmployee
    # end if

    if form.ShowData():
      uipTran = self.uipTransaction
      uipTran.EmployeeName = form.uipEmployee.EmployeeName
      uipTran.EmployeeId = form.uipEmployee.EmployeeId
    # end if
    
  def bSearchBudgetClick(self, sender):
    uipTran = self.uipTransaction
    if self.fSearchBudget == None:
      formname = 'Transaksi/fSelectBudgetYear'
      form = self.app.CreateForm(formname,formname,0,None,None)
      self.fSearchBudget = form
    else:
      form = self.fSearchBudget
    # end if

    BranchCode = uipTran.BranchCode
    PeriodId = uipTran.PeriodId
    if form.GetBudgetCode(BranchCode,PeriodId):
      uipTran.Edit()
      uipTran.BudgetCode = form.BudgetCode
      uipTran.BudgetOwner = form.OwnerName
      uipTran.BudgetId = form.BudgetId
    # end if

  def CheckRequired(self):
    app = self.app
    uipTran = self.uipTransaction

    self.FormObject.CommitBuffer()

    if uipTran.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'

    if uipTran.GetFieldValue('LCashAccount.AccountNo') in ['',None] :
      raise 'PERINGATAN','Kas /Bank belum dipilih'
      
    if uipTran.GetFieldValue('LInvoiceFA.InvoiceId') in ['',None] :
      raise 'PERINGATAN','Invoice belum dipilih'

    if (uipTran.Amount or 0.0) <= 0.0:
      raise 'PERINGATAN','Nilai invoice belum diinputkan'
    
  def bSimpanClick(self, sender):
    app = self.app

    self.CheckRequired()
    
    if app.ConfirmDialog('Yakin simpan transaksi ?'):
      self.FormObject.CommitBuffer()

      ph = self.FormObject.GetDataPacket()

      ph = self.FormObject.CallServerMethod("SimpanData", ph)
      res = ph.FirstRecord
      if res.IsErr == 1:
        app.ShowMessage(res.ErrMessage)
        sender.ExitAction = 0
      else:
        Message = 'Transaksi Berhasil.\nNomor Transaksi : ' + res.TransactionNo
        if res.IsErr == 2:
          Message += '\n Proses Jurnal Gagal.' + res.ErrMessage

        app.ShowMessage(Message)
        #if app.ConfirmDialog('Apakah akan cetak kwitansi ?'):
        #  oPrint = app.GetClientClass('PrintLib','PrintLib')()
        # oPrint.doProcessByStreamName(app,ph.packet,res.StreamName)

        sender.ExitAction = 1
    #-- if
