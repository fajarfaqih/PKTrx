MAPEntity = {'Z': 1, 'I': 2, 'W': 3}

class fInvoicePayment :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.form = formObj
    self.fSearchInvoice = None
    self.RefTransactionNo = None

  def InitValues(self):
    self.fSelectProduct = None
    self.fSelectGL = None
    self.fSelectBudget = None


  def Show(self,mode = 1):
    self.uipTransaction.Edit()
    self.uipTransaction.ShowMode = mode
    self.InitValues()
    return self.FormContainer.Show()

  def RefTransactionNoOnExit(self,sender):
    app = self.app
    uipTran = self.uipTransaction
    
    EmployeeId = uipTran.EmployeeId or ''
    RefTransactionNo = uipTran.RefTransactionNo or ''
    if ( EmployeeId == '' or
         RefTransactionNo ==  '' or
         ( RefTransactionNo != ''
           and self.RefTransactionNo == RefTransactionNo)
       ) : return

    ph = app.CreateValues(
            ['TransactionNo',RefTransactionNo],
            ['EmployeeId',EmployeeId],
        )

    rph = self.form.CallServerMethod('GetInfoRefTransaction',ph)
    
    rec = rph.FirstRecord
    if rec.Is_Err :
      uipTran.RefAmount = 0.0
      uipTran.Amount = 0.0
      uipTran.RefTransactionDate = None
      uipTran.RefDescription = ''
      uipTran.RefTransactionItemId = 0
      self.RefTransactionNo = None
      raise 'PERINGATAN',rec.Err_Message
      
    uipTran.Edit()
    uipTran.RefAmount = rec.Amount
    uipTran.Amount = rec.InvoiceAmount
    uipTran.RefTransactionDate = rec.InvoiceDate
    uipTran.RefDescription = rec.Description
    #uipTran.RefTransactionItemId = rec.TransactionItemId
    self.RefTransactionNo = RefTransactionNo

  def bCariClick(self, sender):
    if self.fSearchInvoice == None :
      formname ='Transaksi/fSelectInvoice'
      form = self.app.CreateForm(formname,formname,0,None,None)
      self.fSearchInvoice = form
    else :
      form = self.fSearchInvoice
      
    if form.GetTransaction(self.uipTransaction.BranchCode):
      uipInv = form.uipInvoice
      
      uipTran = self.uipTransaction
      uipTran.Edit()
      uipTran.RefAmount = uipInv.InvoiceAmount
      uipTran.Amount = uipInv.InvoiceAmount
      uipTran.RefTransactionDate = uipInv.InvoiceDate
      
      uipTran.InvoiceId = uipInv.InvoiceId
      uipTran.RefInvoiceNo = uipInv.InvoiceNo
      uipTran.RefSponsorId = uipInv.GetFieldValue('LSponsor.Id')
      uipTran.RefSponsorName = uipInv.GetFieldValue('LSponsor.Full_Name')
      uipTran.RefProductName = uipInv.GetFieldValue('LProductAccount.AccountName')
      uipTran.RefProductNo = uipInv.GetFieldValue('LProductAccount.AccountNo')
      uipTran.RefCurrencyCode = uipInv.GetFieldValue('LCurrency.Currency_Code')
      uipTran.RefCurrencyName = uipInv.GetFieldValue('LCurrency.Short_Name')
      uipTran.RefRate = uipInv.GetFieldValue('LCurrency.Kurs_Tengah_BI')
      uipTran.PercentageOfAmil = uipInv.GetFieldValue('LProductAccount.LProduct.PercentageOfAmilFunds')
      uipTran.Description = uipInv.Description
      self.SetEkuivalenAmount()

  def CheckRequired(self):
    app = self.app
    form = self.form
    uipTran = self.uipTransaction
    
    form.CommitBuffer()
    
    # Cek Tanggal Transaksi
    if uipTran.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'
      
    # Cek Invoice
    if uipTran.InvoiceId in [None, 0] :
      raise 'PERINGATAN','Anda belum memilih no Invoice'
      
    # Cek Cash Account
    AccountNo = uipTran.GetFieldValue('LCashAccount.AccountNo') or ''
    if AccountNo == '' :
      raise 'PERINGATAN','Anda belum memilih rekening kas/bank'
    
  def RateOnExit(self,sender):
    self.SetEkuivalenAmount()

  def SetEkuivalenAmount(self):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.RefAmountEkuivalen = (uipTran.RefRate or 1.0) * (uipTran.RefAmount or 0.0)

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

        if app.ConfirmDialog('Apakah akan cetak kwitansi ?'):
          oPrint = app.GetClientClass('PrintLib','PrintLib')()
          oPrint.doProcessByStreamName(app,ph.packet,res.StreamName)
          
        sender.ExitAction = 1
    #-- if

