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


  def CreateReturnTrans(self,TransactionNo):
    self.GetRefTransactionByNo(TransactionNo)
    
    st = self.FormContainer.Show()
    if st == 1 :
      return 1
    else:
      return 2
    
    
  def Show(self,mode = 1):
    self.uipTransaction.Edit()
    self.uipTransaction.ShowMode = mode
    self.InitValues()
    return self.FormContainer.Show()

  def JenisTransaksiOnChange(self,sender):
    uip = self.uipTransaction
    uip.Edit()
    uip.TransactionNo = KodeTransaksi[sender.ItemIndex] + uip.TransactionNo[2:]
    
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

  def GetRefTransactionByNo(self,TransactionNo):
    app = self.app
    uipTran = self.uipTransaction
    
    ph = app.CreateValues(['TransactionNo',TransactionNo])
    rph = self.form.CallServerMethod('GetInfoRefTransaction',ph)
    
    status = rph.FirstRecord

    if status.Is_Err :
      uipTran.RefTransactionNo = TransactionNo
      uipTran.RefAmount = 0.0
      uipTran.Amount = 0.0
      uipTran.TotalAmount = 0.0
      uipTran.RefTransactionDate = 0
      uipTran.RefDescription = ''
      uipTran.RefTransactionId = 0

      uipTran.BranchCodeDestination = ''
      
      uipTran.SetFieldValue('LCashAccountDestination.AccountNo','')
      uipTran.SetFieldValue('LCashAccountDestination.AccountName','')
      uipTran.SetFieldValue('LCashAccountSource.AccountNo','')
      uipTran.SetFieldValue('LCashAccountSource.AccountName','')
      self.RefTransactionNo = ''

      raise 'PERINGATAN',status.Err_Message
    
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.RefTransactionNo = TransactionNo
    uipTran.RefAmount = status.Amount
    uipTran.Amount = status.Amount
    uipTran.TotalAmount = 0.0
    uipTran.RefTransactionDate = status.TransactionDate
    uipTran.RefDescription = status.Description
    uipTran.RefTransactionId = status.TransactionId
    
    uipTran.BranchCodeDestination = status.BranchCodeDestination
    uipTran.BranchCodeSource = status.BranchCodeSource
    uipTran.SetFieldValue('LCashAccountDestination.AccountNo',status.DestAccountNo)
    uipTran.SetFieldValue('LCashAccountDestination.AccountName',status.DestAccountName)
    uipTran.SetFieldValue('LCashAccountSource.AccountNo',status.SourceAccountNo)
    uipTran.SetFieldValue('LCashAccountSource.AccountName',status.SourceAccountName)

    self.RefTransactionNo = uipTran.RefTransactionNo

  def RefTransactionNoOnExit(self,sender):
    app = self.app

    TransactionNo = self.uipTransaction.RefTransactionNo or ''
    if TransactionNo == '' : return
    self.GetRefTransactionByNo(TransactionNo)

  def bCariClick(self, sender):
    if self.fSearchCATrans == None :
      #formname ='Transaksi/fSelectTransactionBranchDist'
      formname = 'Transaksi/fSelectDistributionTransfer'
      
      fTrans = self.app.CreateForm(formname,formname,0,None,None)
      self.fSelectTransaction = fTrans
    else :
      fTrans = self.fSelectTransaction
      
    if fTrans.GetTransaction('OUT'):
      #uipCA = fTrans.uipCATransactItem
      uipCA = fTrans.uipDistributionList
      
      uipTran = self.uipTransaction
      uipTran.Edit()
      uipTran.RefTransactionNo = uipCA.TransactionNo
      uipTran.RefAmount = uipCA.Amount
      uipTran.Amount = uipCA.Amount
      uipTran.TotalAmount = 0.0
      uipTran.RefTransactionDate = uipCA.TransactionDate
      uipTran.RefDescription = uipCA.Description
      uipTran.RefTransactionId = uipCA.TransactionId
      uipTran.BranchCodeDestination = uipCA.BranchCodeDest
      uipTran.BranchCodeSource = uipCA.BranchCodeSource
      uipTran.SetFieldValue('LCashAccountDestination.AccountNo',uipCA.DestCashAccountNo)
      uipTran.SetFieldValue('LCashAccountDestination.AccountName',uipCA.DestCashAccountName)
      uipTran.SetFieldValue('LCashAccountSource.AccountNo',uipCA.SourceCashAccountNo)
      uipTran.SetFieldValue('LCashAccountSource.AccountName',uipCA.SourceCashAccountName)
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

  def CheckRefTransaction(self):
    if (self.uipTransaction.RefTransactionId or 0) == 0 :
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
    
  def ItemNewRecord (self, sender):
    sender.ItemIdx = self.IdxCounter
    sender.Amount = 0.0
    sender.AmountBefore = 0.0
    sender.Rate   = 1.0
    sender.Ekuivalen = 0.0

  def ItemBeforePost(self, sender) :
    aProductId = sender.GetFieldValue('LProduct.ProductId')
    #if aProductId == None or aProductId == 0:
    #  raise 'Produk', 'Produk belum dipilih'
      #self.app.ShowMessage('Produk belum dipilih')
      #sender.Cancel()

    if sender.Amount <= 0.0 :
      raise 'Nilai Transaksi', 'Nilai transaksi tidak boleh negatif atau 0.0'

    sender.Ekuivalen = sender.Amount * (sender.Rate or 1.0)
    #fundCategory = self.uipTransactionItem.GetFieldValue('LProduct.FundCategory')
    fundEntity = self.uipTransactionItem.FundEntity
    #if fundCategory == 'Z' and sender.Ashnaf == 'L':
    if sender.ItemType == 'D' :
      pass
      #if fundEntity == 1 and sender.Ashnaf == 'L':
      #  raise 'Ashnaf', 'Ashnaf zakat harus diisi'
      #elif fundEntity != 1: # fundCategory != 'Z'
      #  sender.Ashnaf = 'L'
    else:
      sender.Ashnaf = 'N'
      sender.FundEntity = 0

    if (self.uipTransaction.Amount - (sender.Ekuivalen - sender.AmountBefore)) < 0.0 :
      raise 'Nilai Transaksi','Nilai transaksi melebihi outstanding pemberian'

    sender.AmountBefore = sender.Amount
    
  def ItemAfterPost(self, sender) :
    self.IdxCounter += 1

    Idx = sender.ItemIdx
    if self.AmountList.has_key(Idx):
      amountbefore = self.AmountList[Idx]
    else:
      amountbefore = 0.0
    self.AmountList[Idx] = sender.Ekuivalen

    self.uipTransaction.Edit()
    self.uipTransaction.Amount -= (sender.Ekuivalen - amountbefore)
    self.uipTransaction.TotalAmount += (sender.Ekuivalen - amountbefore)
    self.uipTransaction.Post()

  def ItemBeforeDelete(self,sender):
    self.uipTransaction.Edit()
    self.uipTransaction.Amount += sender.Ekuivalen
    self.uipTransaction.TotalAmount -= sender.Ekuivalen
    self.uipTransaction.Post()

  def ValidationBeforeSave(self):
    uipTran = self.uipTransaction
    
    self.FormObject.CommitBuffer()
    
    self.CheckRefTransaction()
    
    if uipTran.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'

    CashAccountNo = uipTran.GetFieldValue('LCashAccount.AccountNo') or ''
    
    if CashAccountNo == '':
      raise 'PERINGATAN','Anda Belum Memilih Kas/Bank pengembalian dana'
    


