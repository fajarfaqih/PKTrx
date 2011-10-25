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

    if self.uipTransaction.ShowMode == 1 : # insert
      self.AmountList = {}
      self.IdxCounter = 1
    else: # edit mode
      self.AmountList = {}

      idx = 1
      uipItem = self.uipTransactionItem
      uipItem.First()
      TotalItemRow = uipItem.RecordCount
      for i in range(TotalItemRow):
        self.AmountList[uipItem.ItemIdx] = uipItem.Amount #uipItem.Ekuivalen
        idx +=1
      # end for
      self.IdxCounter = TotalItemRow + 1


  def Show(self,mode = 1):
    self.uipTransaction.Edit()
    self.uipTransaction.ShowMode = mode
    self.InitValues()
    return self.FormContainer.Show()

  def JenisTransaksiOnChange(self,sender):
    uip = self.uipTransaction
    uip.Edit()
    uip.TransactionNo = KodeTransaksi[sender.ItemIndex] + uip.TransactionNo[2:]
    
  def EmployeeAfterLookup (self, sender, linkui):
    #self.uipTransaction.EmployeeName = self.uipTransaction.GetFieldValue('LEmployee.Nama_Lengkap')
    #self.uipTransaction.EmployeeId = self.uipTransaction.GetFieldValue('LEmployee.Nomor_Karyawan')
    self.uipTransaction.EmployeeName = self.uipTransaction.GetFieldValue('LEmployee.AccountName')
    self.uipTransaction.EmployeeId = self.uipTransaction.GetFieldValue('LEmployee.EmployeeIdNumber')
    #self.uipTransaction.EmployeeId = self.uipTransaction.GetFieldValue('LEmployee.Nomor_Karyawan')


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
      uipCA = form.uipInvoice
      
      uipTran = self.uipTransaction
      uipTran.Edit()
      uipTran.RefAmount = uipCA.InvoiceAmount
      uipTran.Amount = uipCA.InvoiceAmount
      uipTran.RefTransactionDate = uipCA.InvoiceDate
      
      uipTran.InvoiceId = uipCA.InvoiceId
      uipTran.RefInvoiceNo = uipCA.InvoiceNo
      uipTran.RefSponsorId = uipCA.GetFieldValue('LSponsor.Id')
      uipTran.RefSponsorName = uipCA.GetFieldValue('LSponsor.Full_Name')
      uipTran.RefProductName = uipCA.GetFieldValue('LProductAccount.AccountName')
      uipTran.RefProductNo = uipCA.GetFieldValue('LProductAccount.AccountNo')

  def bSimpanClick(self, sender):
    app = self.app
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

  def CheckRefTransaction(self):
    if (self.uipTransaction.RefTransactionItemId or 0) == 0 :
      raise 'PERINGATAN','Pilih / Isi Dahulu Ref. Transaksi Penyerahan'


  def InsertProductClick(self,sender) :
    self.CheckRefTransaction()
    self.OpenFormProduct()

  def GetFormProduct(self):
    app = self.app
    if self.fSelectProduct == None:
      form = app.CreateForm('Transaksi/fCARProduct','Transaksi/fCARProduct',0,None,None)
      self.fSelectProduct = form
    else :
      form = self.fSelectProduct
    return form

  def SetProductItem(self,uipTranItem,uipData):
    uipTranItem.AccountId = uipData.GetFieldValue('LProductAccount.AccountNo')
    uipTranItem.AccountName = uipData.GetFieldValue('LProductAccount.AccountName')
    uipTranItem.FundEntity = uipData.FundEntity or 'I'
    #uipTranItem.BudgetCode = uipData.BudgetCode
    uipTranItem.BudgetCode = uipData.GetFieldValue('LBudget.BudgetCode')
    uipTranItem.BudgetOwner = uipData.GetFieldValue('LBudget.LOwner.OwnerName')
    uipTranItem.Ashnaf = uipData.Ashnaf
    uipTranItem.Amount = uipData.Amount
    uipTranItem.Description = uipData.Description
    uipTranItem.ItemType = 'D'

  def OpenFormProduct(self):
    app = self.app
    
    form = self.GetFormProduct()
    if form.GetData():
      uipData = form.uipData
      uipTranItem = self.uipTransactionItem
      uipTranItem.Append()
      self.SetProductItem(uipTranItem,uipData)
      uipTranItem.Post()

  def InsertGLClick(self,sender):
    self.CheckRefTransaction()
    self.OpenFormGL()
    
  def GetFormGL(self):
    app = self.app
    if self.fSelectGL == None:
      form = app.CreateForm('Transaksi/fCARGL','Transaksi/fCARGL',0,None,None)
      self.fSelectGL = form
    else :
      form = self.fSelectGL

    return form

  def SetGLItem(self,uipTranItem,uipData):
    uipTranItem.AccountId = uipData.GetFieldValue('LLedger.Account_Code')
    uipTranItem.AccountName = uipData.GetFieldValue('LLedger.Account_Name')
    #uipTranItem.BudgetCode = uipData.BudgetCode
    uipTranItem.Amount = uipData.Amount
    uipTranItem.Description = uipData.Description
    uipTranItem.BudgetCode = uipData.GetFieldValue('LBudget.BudgetCode')
    uipTranItem.BudgetOwner = uipData.GetFieldValue('LBudget.LOwner.OwnerName')
    uipTranItem.ItemType = 'G'

  def OpenFormGL(self):
    app = self.app

    form = self.GetFormGL()
    if form.GetData():
      uipData = form.uipData
      uipTranItem = self.uipTransactionItem
      uipTranItem.Append()
      self.SetGLItem(uipTranItem,uipData)
#      uipTranItem.AccountId = uipData.GetFieldValue('LLedger.Account_Code')
#      uipTranItem.AccountName = uipData.GetFieldValue('LLedger.Account_Name')
#      uipTranItem.BudgetCode = uipData.BudgetCode
#      uipTranItem.Amount = uipData.Amount
#      uipTranItem.Description = uipData.Description
#      uipTranItem.ItemType = 'G'
      uipTranItem.Post()

  def CheckDetail(self):
    if self.uipTransactionItem.ItemType in ['',None] :
      raise 'PERINGATAN','Tidak ada data yang dipilih'

  def EditTransClick(self,sender):
    self.CheckDetail()
    self.OpenEditClick()

  def OpenEditClick(self):
    app = self.app

    uipItem = self.uipTransactionItem
    if uipItem.ItemType == 'D':
      form = self.GetFormProduct()
    else : # uipItem.ItemType == 'G'
      form = self.GetFormGL()

    if form.GetData(1,uipItem):
      uipData = form.uipData
      uipItem.Edit()
      if uipItem.ItemType == 'D':
        self.SetProductItem(uipItem,uipData)
      else : # uipItem.ItemType == 'G'
        self.SetGLItem(uipItem,uipData)
      # if else
      uipItem.Post()
      
  def DeleteTransClick(self,sender):
    self.DeleteTransaction()
    
  def DeleteTransaction(self):
    self.CheckDetail()
    self.uipTransactionItem.Delete()
