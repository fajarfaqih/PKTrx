MAPEntity = {'Z': 1, 'I': 2, 'W': 3}

class fCashAdvanceReturn :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.form = formObj
    self.fSearchEmployee = None
    self.RefTransactionNo = None
    
  def InitValues(self):
    self.fSearchCATrans = None
    self.fSelectProduct = None
    self.fSelectGL = None
    self.fSelectBudget = None

    if self.uipTransaction.ShowMode == 1 : # insert mode
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

  def bSearchEmployeeClick(self,sender):
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

  def BudgetBeforeLookUp(self,sender,linkui):
    if self.fSelectBudget == None :
      formname = 'Transaksi/fSelectBudgetCode'
      fSelectBudget = self.app.CreateForm(formname,formname,0,None, None)
      self.fSelectBudget = fSelectBudget

    if self.fSelectBudget.GetBudget(self.uipTransaction.PeriodId) == 1:
      BudgetCode = self.fSelectBudget.BudgetCode
      BudgetId = self.fSelectBudget.BudgetId
      BudgetOwner = self.fSelectBudget.BudgetOwner

      self.uipTransactionItem.Edit()
      self.uipTransactionItem.BudgetCode = BudgetCode
      self.uipTransactionItem.BudgetId = BudgetId
      self.uipTransactionItem.BudgetOwner = BudgetOwner

  def ProductBeforeLookup(self, sender, linkui):
    if self.fSelectProduct == None:
      fData = self.app.CreateForm('Transaksi/fSelectProduct', 'Transaksi/fSelectProduct', 0, None, None)
      self.fSelectProduct = fData
    else:
      fData = self.fSelectProduct

    branchCode = self.uipTransaction.BranchCode
    if fData.GetProduct(branchCode) == 1:
      productId = fData.ProductId
      productName = fData.ProductName
      fundCategory = fData.FundCategory
      fundEntity = MAPEntity[fData.FundCategory or 'I']

      self.uipTransactionItem.Edit()
      self.uipTransactionItem.SetFieldValue('LProduct.ProductId', productId)
      self.uipTransactionItem.SetFieldValue('LProduct.ProductName', productName)
      self.uipTransactionItem.SetFieldValue('LProduct.FundCategory', fundCategory)
      self.uipTransactionItem.FundEntity = fundEntity

      if fundEntity != 1:
        self.uipTransactionItem.Ashnaf = 'L'

    return 1

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
    uipTran.Amount = rec.Amount
    uipTran.RefTransactionDate = rec.TransactionDate
    uipTran.RefDescription = rec.Description
    uipTran.RefTransactionItemId = rec.TransactionItemId
    self.RefTransactionNo = RefTransactionNo

  def TotalAmountOnExit(self,sender):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.Amount = uipTran.RefAmount - uipTran.TotalAmount

  def bCariClick(self, sender):
    EmployeeId = self.uipTransaction.EmployeeId or 0
    if EmployeeId == 0 :
      raise 'PERINGATAN','Pilih dahulu nomor karyawan'
      
    if self.fSearchCATrans == None :
      formname ='Transaksi/fSelectTransactionCashAdvance'
      fTrans = self.app.CreateForm(formname,formname,0,None,None)
      self.fSelectTransaction = fTrans
    else :
      fTrans = self.fSelectTransaction
      
    if fTrans.GetTransaction(EmployeeId):
      uipCA = fTrans.uipCATransactItem
      
      uipTran = self.uipTransaction
      uipTran.Edit()
      uipTran.RefTransactionNo = uipCA.TransactionNo
      uipTran.RefAmount = uipCA.Amount
      uipTran.Amount = uipCA.Amount
      uipTran.TotalAmount = 0.0
      uipTran.RefTransactionDate = uipCA.TransactionDate
      uipTran.RefDescription = uipCA.Description
      uipTran.RefTransactionItemId = uipCA.TransactionItemId
      self.RefTransactionNo = uipTran.RefTransactionNo

    
  def bSimpanClick(self, sender):
    app = self.app
    
    self.ValidationBeforeSave()

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

  def ValidationBeforeSave(self):
    uipTran = self.uipTransaction

    self.FormObject.CommitBuffer()

    self.CheckRefTransaction()

    #BatchId = uipTran.GetFieldValue('LBatch.BatchId') or 0

    #if BatchId == 0 :
    #  raise 'PERINGATAN','Anda Belum Memilih Batch'
    if uipTran.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'


    CashAccountNo = uipTran.GetFieldValue('LCashAccount.AccountNo') or ''

    if CashAccountNo == '':
      raise 'PERINGATAN','Anda Belum Memilih Kas/Bank pengembalian dana'

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

