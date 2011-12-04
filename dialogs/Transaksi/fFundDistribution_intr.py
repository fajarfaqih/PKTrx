# GLOBALs
MAPEntity = {'Z': 1, 'I': 2, 'W': 3}

DefaultItems = [ 'Inputer',
                 'BranchCode',
                 'TransactionDate',
                 'FloatTransactionDate',
                 'Rate',
                 'TotalAmount',
                 'CashType',
#                 'LBatch.BatchId',
#                 'LBatch.BatchNo',
#                 'LBatch.Description',
                 'LProductBranch.Kode_Cabang',
                 'LProductBranch.Nama_Cabang',
                 'LValuta.Currency_Code',
                 'LValuta.Full_Name',
                 'LValuta.Kurs_Tengah_BI',
                 'LCurrency.Currency_Code',
                 'LCurrency.Full_Name',
                 'LCurrency.Kurs_Tengah_BI',
                 'LBank.AccountNo',
                 'LBank.BankName',
                 'LBank.CurrencyCode',
                 'PeriodId',
                 'LSponsor.SponsorId',
                 'TransactionNo',
                 'ShowMode',
                 'ActualDate',
                 'ReceivedFrom',
                 ]

class fFundDistribution :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.form = formObj
    self.fSelectProduct = None
    self.fSelectAccount = None
    self.fSelectOwner = None
    self.fSelectItem = None
    self.fSelectBudget = None
    self.fSearchDonor = None
    self.DefaultValues = {}
    self.IdxCounter = 0

  def SaveDefaultValues(self):
    uipTran = self.uipTransaction
    for item in DefaultItems :
      self.DefaultValues[item] = uipTran.GetFieldValue(item)
      
  def ClearData(self):
    self.uipTransaction.ClearData()
    self.uipTransactionItem.ClearData()

    uipTran = self.uipTransaction
    uipTran.Edit()
    for item in DefaultItems :
      uipTran.SetFieldValue(item,self.DefaultValues[item])
    #self.pBatch_LBatch.SetFocus()
    self.pBatch_ActualDate.SetFocus()
    
  def InitValues(self):
    if self.uipTransaction.ShowMode == 1 : # insert mode
      self.AmountList = {}
      self.IdxCounter = 1
    else: # edit mode
      self.AmountList = {}

      uipTran = self.uipTransaction
      uipItem = self.uipTransactionItem

      TotalAmount = 0.0
      TotalItemRow = uipItem.RecordCount
      
      Idx = 1
      uipItem.First()
      for i in range(TotalItemRow):
        uipItem.Edit()

        # Assign Ulang Index Grid
        uipItem.ItemIdx = Idx
        
        # Simpan Nilai Amount Sebagai Helper
        self.AmountList[uipItem.ItemIdx] = uipItem.Amount #uipItem.Ekuivalen
        
        # Hitung Ulang Total Penyaluran
        TotalAmount += uipItem.Amount
        
        Idx += 1
        uipItem.Next()
      # end for

      # Set IdxCounter sebagai helper
      self.IdxCounter = TotalItemRow + 1

      # Hitung Ulang Total Penyaluran
      uipTran.Edit()
      uipTran.TotalAmount = TotalAmount

  # mode
  # 1 : input mode
  # 2 : edit mode
  def Show(self,mode=1):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.ShowMode = mode
    self.InitValues()

    if mode == 1:
      # Insert Mode
      self.SaveDefaultValues()
      
    else:
      # Edit Mode
      
      #self.pBatch_LBatch.Enabled = 0
      # Set Save button hidden
      self.pAction_bSave.Visible = 0

      # Move button position
      self.pAction_bCancel.Left = self.pAction_bSimpanClose.Left
      self.pAction_bSimpanClose.Left = self.pAction_bSave.Left
      
      PageIndex = {'C' : 0 , 'K' : 0 ,'B' : 1 , 'A':2}
      self.mpBayar.ActivePageIndex = PageIndex[uipTran.PaymentType]
      
    return self.FormContainer.Show()
    
  def BatchAfterLookup(self, sender, linkui):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.ActualDate = uipTran.GetFieldValue('LBatch.BatchDate')
    self.DefaultValues['LBatch.BatchId'] = uipTran.GetFieldValue('LBatch.BatchId')
    self.DefaultValues['LBatch.BatchNo'] = uipTran.GetFieldValue('LBatch.BatchNo')
    self.DefaultValues['LBatch.Description'] = uipTran.GetFieldValue('LBatch.Description')
    self.DefaultValues['ActualDate'] = uipTran.ActualDate

  def CashCurrAfterLookup(self, sender, linkui):
    uipItem = self.uipTransactionItem
    uipItem.Edit()
    uipItem.Rate = uipItem.GetFieldValue('LCurrency.Kurs_Tengah_BI')

  def ProductBeforeLookup(self, sender, linkui):
    if self.fSelectProduct == None:
      fData = self.app.CreateForm('Transaksi/fSelectProgram', 'Transaksi/fSelectProgram', 0, None, None)
      self.fSelectProduct = fData
    else:
      fData = self.fSelectProduct
    branchCode = self.uipTransaction.BranchCode #GetFieldValue('LProductBranch.Kode_Cabang')
    if fData.GetProduct(branchCode) == 1:
      productId = fData.ProductId
      productName = fData.ProductName
      fundCategory = fData.FundCategory
      AccountNo = fData.AccountNo
      fundEntity = MAPEntity[fData.FundCategory or 'I']

      self.uipTransactionItem.Edit()
      self.uipTransactionItem.SetFieldValue('LProduct.ProductId', productId)
      self.uipTransactionItem.SetFieldValue('LProduct.ProductName', productName)
      self.uipTransactionItem.SetFieldValue('LProduct.FundCategory', fundCategory)
      self.uipTransactionItem.FundEntity = fundEntity
      self.uipTransactionItem.AccountNo = AccountNo
      self.uipTransactionItem.Description = productName

      if fundEntity != 1:
        self.uipTransactionItem.Ashnaf = 'L'

    return 1

  def OwnerBeforeLookup(self, sender, linkui):
    ItemCode = self.uipTransactionItem.DistItemCode or 0
    PeriodId = self.uipTransaction.PeriodId or 0
    if self.fSelectOwner == None:
      fData = self.app.CreateForm('Transaksi/fSelectBudgetOwner', 'Transaksi/fSelectBudgetOwner', 0, None, None)
      self.fSelectOwner = fData
    else:
      fData = self.fSelectOwner

    if fData.GetOwner(ItemCode,PeriodId) == 1:
      self.uipTransactionItem.Edit()
      self.uipTransactionItem.OwnerId = fData.OwnerId
      self.uipTransactionitem.BudgetCode = fData.BudgetCode
      self.uipTransactionItem.OwnerName = fData.OwnerName
      self.uipTransactionitem.BudgetId = fData.BudgetId
    #-- if

  def CurrencyAfterLookup(self,sender,linkui):
    uipTransaction = self.uipTransaction
    if uipTransaction.GetFieldValue('LCurrency.Currency_Code') != None :
       uipTransaction.Edit()
       uipTransaction.Rate = uipTransaction.GetFieldValue('LCurrency.Kurs_Tengah_BI')


  def BankAfterLookup(self,sender,linkui):
    app = self.app
    uipTran = self.uipTransaction

    CurrencyCode = uipTran.GetFieldValue('LBank.CurrencyCode')

    param = app.CreateValues(['CurrencyCode',CurrencyCode])
    rph = self.form.CallServerMethod('GetCurrencyRate',param)

    rec = rph.FirstRecord
    uipTran.CurrencyCode = CurrencyCode
    uipTran.Rate = rec.Kurs_Tengah_BI

    self.DefaultValues['LBank.AccountNo'] = uipTran.GetFieldValue('LBank.AccountNo')
    self.DefaultValues['LBank.BankName'] = uipTran.GetFieldValue('LBank.BankName')
    self.DefaultValues['LBank.CurrencyCode'] = uipTran.GetFieldValue('LBank.CurrencyCode')

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

  def DistItemBeforeLookup(self, sender, linkui):
    OwnerId = self.uipTransactionItem.OwnerId or 0
    PeriodId = self.uipTransaction.PeriodId or 0
    if OwnerId == 0 :
      raise 'Peringatan','Data Kode Pemilik Anggaran Belum Dipilih.\n Silahkan pilih pemilik anggaran lebih dahulu'
    
    if self.fSelectItem == None:
      fData = self.app.CreateForm('Transaksi/fSelectBudgetItem', 'Transaksi/fSelectBudgetItem', 0, None, None)
      self.fSelectItem = fData
    else:
      fData = self.fSelectItem

    if fData.GetItem(OwnerId,PeriodId) == 1:
      self.uipTransactionItem.Edit()
      self.uipTransactionItem.DistItemCode = fData.Account_Code
      self.uipTransactionItem.DistItemName = fData.Account_Name
    #-- if

    return 1

  def ItemNewRecord (self, sender):
    sender.ItemIdx = self.IdxCounter
    sender.Amount = 0.0


  def ItemBeforePost(self, sender) :
    aProductId = sender.GetFieldValue('LProduct.ProductId')
    if aProductId == None or aProductId == 0:
      raise 'Produk', 'Produk belum dipilih'
      #self.app.ShowMessage('Produk belum dipilih')
      #sender.Cancel()

    if sender.Amount <= 0.0 :
      raise 'Nilai Transaksi', 'Nilai transaksi tidak boleh negatif atau 0.0'
      
    #sender.Ekuivalen = sender.Amount * sender.Rate
    #fundCategory = self.uipTransactionItem.GetFieldValue('LProduct.FundCategory')
    fundEntity = self.uipTransactionItem.FundEntity
    #if fundCategory == 'Z' and sender.Ashnaf == 'L':
    if fundEntity == 1 and sender.Ashnaf == 'L':
      raise 'Ashnaf', 'Ashnaf zakat harus diisi'
    elif fundEntity != 1: # fundCategory != 'Z'
      sender.Ashnaf = 'L'

  def ItemBeforeDelete(self,sender):
    self.uipTransaction.Edit()
    self.uipTransaction.TotalAmount -= sender.Amount
    self.uipTransaction.Post()
    
  def ItemAfterPost(self, sender) :
    self.IdxCounter += 1

    Idx = sender.ItemIdx
    if self.AmountList.has_key(Idx):
      amountbefore = self.AmountList[Idx]
    else:
      amountbefore = 0.0
    self.AmountList[Idx] = sender.Amount

    self.uipTransaction.Edit()
    self.uipTransaction.TotalAmount += (sender.Amount - amountbefore)
    self.uipTransaction.Post()

  def bCancelClick(self, sender):
    if self.app.ConfirmDialog('Yakin batalkan transaksi ?'):
      sender.ExitAction = 1
    else:
      sender.ExitAction = 0

  def CheckRequiredBank(self):
    if self.uipTransaction.GetFieldValue('LBank.AccountNo') == None:
      self.app.ShowMessage('Bank belum dipilih')
      return 0
    else:
      return 1

  def CheckRequiredAsset(self):
    if (self.uipTransaction.GetFieldValue('LAsset.Account_Code') == None or
      self.uipTransaction.GetFieldValue('LValuta.Currency_Code') == None):
      self.app.ShowMessage('Asset/Valuta belum dipilih')
      return 0
    else:
      return 1

  def CheckRequiredGeneral(self):
    uipTran  = self.uipTransaction
    #if self.uipTransaction.GetFieldValue('LBatch.BatchId') == None:
    #  self.app.ShowMessage('Batch belum dipilih')
    #  return 0
    
    if uipTran.ActualDate in [0, None] :
      self.app.ShowMessage('Tanggal Transaksi belum diinputkan')
      return 0

    if self.uipTransactionItem.RecordCount <= 0 :
      self.app.ShowMessage('Detail Transaksi belum diinput')
      return 0

#    ReferenceNo = uipTran.ReferenceNo or ''
#    pType = self.mpBayar.ActivePageIndex
#    if (ReferenceNo == '' and pType != 1 ) :
#      self.app.ShowMessage('No. Referensi/FSZ Belum Diinput')
#      return 0

    return 1
    
  def SponsorClick(self,sender):
    if self.fSearchDonor == None :
      fSearch = self.app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
      self.fSearchDonor = fSearch
    else :
      fSearch = self.fSearchDonor

    if fSearch.GetDonorData():
      uipTran = self.uipTransaction
      uipTran.Edit()

      uipTran.DonorId = fSearch.DonorIntId
      uipTran.DonorNo = fSearch.DonorNo
      uipTran.DonorName = fSearch.DonorName

  def bSimpanClick(self, sender):
    if self.Simpan(1):
      self.ClearData()
    
  def bSimpanCloseClick(self,sender):
    if self.Simpan(2):
      sender.ExitAction = 1

  def Simpan(self, savemode):
    app = self.app

    self.FormObject.CommitBuffer()
    if not self.CheckRequiredGeneral(): return 0
    
    if self.app.ConfirmDialog('Yakin simpan transaksi ?'):
      uipTran = self.uipTransaction
      uipTran.Edit()
      uipTran.SaveMode = savemode
      pType = self.mpBayar.ActivePageIndex
      if pType == 0:
        uipTran.PaymentType = uipTran.CashType
      elif pType == 1:
        uipTran.PaymentType = 'B'
        if not self.CheckRequiredBank():
          return 0
      else: #pType == 2:
        uipTran.PaymentType = 'A'
        if not self.CheckRequiredAsset():
          return 0

      self.FormObject.CommitBuffer()
      ph = self.FormObject.GetDataPacket()

      ph = self.FormObject.CallServerMethod("SimpanData", ph)
      res = ph.FirstRecord
      if res.IsErr == 1:
        self.app.ShowMessage(res.ErrMessage)
        return 0
      else: # res.IsErr in [0,2]
      
        Message = 'Transaksi Berhasil.\nNomor Transaksi : ' + res.TransactionNo

        if res.IsErr == 2:
          Message += '\n Proses Jurnal Gagal.' + res.ErrMessage
          
        app.ShowMessage(Message)
        
        if savemode == 2 :
          if self.app.ConfirmDialog('Apakah akan cetak kwitansi ?'):
            oPrint = app.GetClientClass('PrintLib','PrintLib')()
            #app.ShowMessage("Masukkan kertas ke printer untuk cetak kwitansi")
            oPrint.doProcessByStreamName(app,ph.packet,res.StreamName)

        #self.DefaultValues['LBatch.BatchId'] = uipTran.GetFieldValue('LBatch.BatchId')
        #self.DefaultValues['LBatch.BatchNo'] = uipTran.GetFieldValue('LBatch.BatchNo')
        self.DefaultValues['ActualDate'] = uipTran.ActualDate
        #if savemode == 1 :
        #  self.DefaultValues['TransactionNo'] = res.NewTransactionNo
      
      return 1
    #-- if
    return 0
