# GLOBALs
MAPEntity = {'Z': 1, 'I': 2, 'W': 3,'A' : 4 , 'N' : 5}
PI_NONE = -1
PI_ITEMS = 0
PI_COLLECTION = 1
PI_DISTRIBUTION = 2
PI_CASH = 3
PI_LEDGER = 4

DefaultItems = [ 'Inputer',
                 'BranchCode',
                 'TransactionDate',
                 'FloatTransactionDate',
                 'TotalDebit',
                 'TotalCredit',
                 'TransactionNo',
                 'ShowMode',
                 #'LBatch.BatchId',
                 #'LBatch.BatchNo',
                 'ActualDate',
#                 'LProductBranch.Kode_Cabang',
#                 'LProductBranch.Nama_Cabang',
#                 'LCurrency.Currency_Code',
#                 'LCurrency.Full_Name',
#                 'LCurrency.Kurs_Tengah_BI',
#                 'LValuta.Currency_Code',
#                 'LValuta.Full_Name',
#                 'LValuta.Kurs_Tengah_BI',
#                 'LBank.AccountNo',
#                 'LBank.BankName',
#                 'LBank.CurrencyCode',
#                 'LSponsor.SponsorId',
#                 'LVolunteer.VolunteerId',
#                 'PaidTo',
                 ]
                 
class fGeneralTransaction :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.form = formObj
    self.DefaultValues = {}
    self.fSelectProduct = None
    self.fSelectProgram = None

  def DisplayPage(self, PageIdx) :
    for i in range(self.mpItem.PageCount):
      self.mpItem.GetPage(i).TabVisible = i == PageIdx

    self.mpItem.ActivePageIndex = PageIdx

  def InitValues(self):
    if self.uipTransaction.ShowMode == 1 : # insert mode
      self.IdxCounter = 1
      self.AmountList = {}
    else: # edit mode
      self.AmountList = {}

      uipItem = self.uipTransactionItem
      uipItem.First()
      TotalItemRow = uipItem.RecordCount

      for i in range(TotalItemRow):
        self.AmountList[uipItem.ItemIdx] = uipItem.MutationType, uipItem.Ekuivalen
        uipItem.Next()
      # end for
      
      self.IdxCounter = TotalItemRow + 1

  def SaveDefaultValues(self):
    uipTran = self.uipTransaction
    for item in DefaultItems :
      self.DefaultValues[item] = uipTran.GetFieldValue(item)
      
  def ClearData(self):
    self.InitValues()
    self.uipTransaction.ClearData()
    self.uipTransactionItem.ClearData()

    uipTran = self.uipTransaction
    uipTran.Edit()
    for item in DefaultItems :
      uipTran.SetFieldValue(item,self.DefaultValues[item])

    #self.pTransaction_LBatch.SetFocus()
    self.pTransaction_ActualDate.SetFocus()
    
  def Show(self,mode=1):
    self.uipTransaction.Edit()
    self.uipTransaction.ShowMode = mode
    self.InitValues()
    self.DisplayPage(PI_ITEMS)
    if mode == 2: # Edit Mode
      self.pItemAction_bSave.Visible = 0
    else:
      self.SaveDefaultValues()
    
    return self.FormContainer.Show()

  def BatchAfterLookup(self, sender, linkui):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.ActualDate = uipTran.GetFieldValue('LBatch.BatchDate')
    self.DefaultValues['LBatch.BatchId'] = uipTran.GetFieldValue('LBatch.BatchId')
    self.DefaultValues['LBatch.BatchNo'] = uipTran.GetFieldValue('LBatch.BatchNo')
    self.DefaultValues['ActualDate'] = uipTran.ActualDate

  def bCollectionClick(self, sender):
    self.uipTransactionItem.Append()
    self.uipTransactionItem.ItemType = 'C'
    self.uipTransactionItem.IsReverseCollection = 'F'
    self.uipTransactionItem.MutationType = 'C'
    self.DisplayPage(PI_COLLECTION)

  def bSearchClick(self, sender) :
    dSearch = self.app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
    donorID = dSearch.GetDonorID()

    if donorID != None:
      self.uipTransactionItem.DonorId = donorID
      self.uipTransactionItem.DonorName = dSearch.DonorName
      
  def SearchProductClick(self,sender):
    if self.fSelectProduct == None:
      fProduct = self.app.CreateForm('Transaksi/fSelectProduct', 'Transaksi/fSelectProduct', 0, None, None)
      self.fSelectProduct = fProduct
    else:
      fProduct = self.fSelectProduct
    # end if
    
    branchCode = self.uipTransaction.BranchCode
    if fProduct.GetProduct(branchCode) == 1:
      productId = fProduct.ProductId
      productName = fProduct.ProductName

      self.uipTransactionItem.Edit()
      self.uipTransactionItem.ProductIdColl = productId
      self.uipTransactionItem.ProductNameColl = productName
      self.uipTransactionItem.ProductCodeColl = productName
      self.uipTransactionItem.FundEntityCollection = MAPEntity[fProduct.FundCategory or 'I']
      self.uipTransactionItem.PercentageOfAmil = fProduct.PercentageOfAmilFunds
      self.uipTransactionItem.AccountNoColl = fProduct.AccountNo
      self.uipTransactionItem.Description = productName

    return 1

  def SearchProgramClick(self,sender):
    if self.fSelectProgram == None:
      fProgram = self.app.CreateForm('Transaksi/fSelectProgram', 'Transaksi/fSelectProgram', 0, None, None)
      self.fSelectProgram = fProgram
    else:
      fProgram = self.fSelectProgram
      
    branchCode = self.uipTransaction.BranchCode
    if fProgram.GetProduct(branchCode) == 1:
      productId = fProgram.ProductId
      productName = fProgram.ProductName
      productCode = fProgram.ProductCode
      AccountNo = fProgram.AccountNo
      fundEntity = MAPEntity[fProgram.FundCategory or 'I']
      self.uipTransactionItem.Edit()
      self.uipTransactionItem.ProductIdDist = productId
      self.uipTransactionItem.ProductNameDist = productName
      self.uipTransactionItem.ProductCodeDist = productCode
      self.uipTransactionItem.FundEntityDist = fundEntity
      self.uipTransactionItem.AccountNoDist = AccountNo
      self.uipTransactionItem.Description = productName

      if fundEntity != 1:
        self.uipTransactionItem.Ashnaf = 'L'

    return 1

  def bSearchSponsorClick(self, sender) :
    dSearch = self.app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
    donorID = dSearch.GetDonorID()

    if donorID != None:
      self.uipTransactionItem.SponsorId = donorID
      self.uipTransactionItem.SponsorName = dSearch.DonorName
      
  def bDistributionClick(self, sender):
    self.uipTransactionItem.Append()
    self.uipTransactionItem.ItemType = 'D'
    self.uipTransactionItem.IsReverseCollection = 'F'
    self.uipTransactionItem.MutationType = 'D'
    self.DisplayPage(PI_DISTRIBUTION)

  def bCashClick(self, sender):
    self.uipTransactionItem.Append()
    self.uipTransactionItem.ItemType = 'B'
    self.DisplayPage(PI_CASH)

  def bLedgerClick(self, sender):
    self.uipTransactionItem.Append()
    self.uipTransactionItem.ItemType = 'G'
    self.DisplayPage(PI_LEDGER)

  def bEditClick(self, sender):
    self.uipTransactionItem.Edit()
    itemType = self.uipTransactionItem.ItemType
    if itemType == 'C':
      self.DisplayPage(PI_COLLECTION)
    elif itemType == 'D':
      self.DisplayPage(PI_DISTRIBUTION)
    elif itemType == 'B':
      self.DisplayPage(PI_CASH)
    else: #itemType == 'G'
      self.DisplayPage(PI_LEDGER)

  def bDeleteClick(self, sender):
    if self.app.ConfirmDialog('Yakin hapus item transaksi ?'):
      self.uipTransactionItem.Delete()

  def SaveItem(self):
    self.uipTransactionItem.Post()
    self.DisplayPage(PI_ITEMS)
    
  def bSaveCollection(self, sender):
    if self.uipTransactionItem.DonorId in (None, ''):
      raise 'Collection', 'Donatur belum diisi!'

    if self.uipTransactionItem.ProductIdColl in (None, 0) :
      raise 'Collection', 'Produk belum diisi!'

    if self.uipTransactionItem.GetFieldValue('ValutaCol.Currency_Code') in (None, 0) :
      raise 'Collection', 'Valuta belum diisi!'

    if self.uipTransactionItem.Amount <= 0.0 :
      raise 'Collection', 'Nilai Transaksi belum diisi!'

    if self.uipTransactionItem.IsReverseCollection == 'T':
      self.uipTransactionItem.MutationType = 'D'
    else:
      self.uipTransactionItem.MutationType = 'C'

    self.SaveItem()

  def bSaveDistribution(self, sender):

    if self.uipTransactionItem.ProductIdDist in (None, 0) :
      raise 'Distribution', 'Produk belum diisi!'

    if self.uipTransactionItem.GetFieldValue('ValutaDist.Currency_Code') in (None, 0) :
      raise 'Distribution', 'Valuta belum diisi!'

    if self.uipTransactionItem.IsReverseDistribution == 'T':
      self.uipTransactionItem.MutationType = 'C'
    else:
      self.uipTransactionItem.MutationType = 'D'
      
      
    self.SaveItem()

  def bSaveCash(self, sender):
    if self.uipTransactionItem.GetFieldValue('LCashAccount.AccountNo') in (None, 0):
      raise 'Collection', 'Kas/Bank belum diisi!'
    self.SaveItem()

  def bSaveLedger(self, sender):
    if (self.uipTransactionItem.GetFieldValue('LLedger.Account_Code') in (None, 0)
      or self.uipTransactionItem.GetFieldValue('ValutaGL.Currency_Code') in (None, 0)):
      raise 'Collection', 'Ledger/Valuta belum diisi!'
    self.SaveItem()

  def bCancelItem(self, sender):
    if self.app.ConfirmDialog('Yakin batalkan item transaksi ?'):
      self.uipTransactionItem.Cancel()
      self.DisplayPage(PI_ITEMS)

  def ItemNewRecord(self, sender) :
    sender.ItemIdx = self.IdxCounter
    sender.CurrencyCode = '000'
    sender.Rate = 1.0

  def ItemBeforePost(self, sender) :
    itemType = sender.ItemType
    if itemType == 'C':
      sender.AccountId = sender.ProductCodeColl #str(sender.GetFieldValue('ProductCol.ProductId'))
      sender.AccountName = str(sender.ProductNameColl) #sender.GetFieldValue('ProductCol.ProductName')
      sender.CurrencyCode = sender.GetFieldValue('ValutaCol.Currency_Code')
    elif itemType == 'D':
      sender.AccountId = sender.ProductCodeDist #str(sender.GetFieldValue('ProductDist.ProductId'))
      sender.AccountName = str(sender.ProductNameDist) #sender.GetFieldValue('ProductDist.ProductName')
      sender.CurrencyCode = sender.GetFieldValue('ValutaDist.Currency_Code')
    elif itemType == 'B':
      sender.AccountId = sender.GetFieldValue('LCashAccount.AccountNo')
      sender.AccountName = sender.GetFieldValue('LCashAccount.AccountName')
      sender.CurrencyCode = sender.GetFieldValue('LCashAccount.CurrencyCode')
    else: # itemType == 'G'
      sender.AccountId = sender.GetFieldValue('LLedger.Account_Code')
      sender.AccountName = sender.GetFieldValue('LLedger.Account_Name')
      sender.CurrencyCode = sender.GetFieldValue('ValutaGL.Currency_Code')

    sender.Ekuivalen = sender.Amount * sender.Rate
    fundEntity = sender.FundEntityDist
    if fundEntity == 1 and sender.Ashnaf == 'L':
      raise 'Ashnaf', 'Ashnaf zakat harus diisi'
    elif fundEntity != 1: # fundCategory != 'Z'
      sender.Ashnaf = 'L'

  def CashAfterLookup(self,sender,linkUI):
    uipTranItem = self.uipTransactionItem
    uipTran = self.uipTransaction

    CurrencyCode = uipTranItem.GetFieldValue('LCashAccount.CurrencyCode')

    param = self.app.CreateValues(['CurrencyCode',CurrencyCode])
    rph = self.form.CallServerMethod('GetCurrencyRate',param)

    rec = rph.FirstRecord
    uipTranItem.Edit()
    uipTranItem.CurrencyCode = CurrencyCode
    uipTranItem.Rate = rec.Kurs_Tengah_BI

  def GLValutaAfterLookUp(self,sender,linkUI):
    uipTranItem = self.uipTransactionItem
    uipTranItem.Edit()
    uipTranItem.CurrencyCode = uipTranItem.GetFieldValue('ValutaGL.Currency_Code')
    uipTranItem.Rate = uipTranItem.GetFieldValue('ValutaGL.Kurs_Tengah_BI')
    
  def ValutaDistAfterLookup(self,sender,linkUI):
    uipTranItem = self.uipTransactionItem
    uipTranItem.Edit()
    uipTranItem.CurrencyCode = uipTranItem.GetFieldValue('ValutaDist.Currency_Code')
    uipTranItem.Rate = uipTranItem.GetFieldValue('ValutaDist.Kurs_Tengah_BI')
    
  def ValutaColAfterLookup(self,sender,linkUI):
    uipTranItem = self.uipTransactionItem
    uipTranItem.Edit()
    uipTranItem.CurrencyCode = uipTranItem.GetFieldValue('ValutaCol.Currency_Code')
    uipTranItem.Rate = uipTranItem.GetFieldValue('ValutaCol.Kurs_Tengah_BI')
    
  def ItemBeforeDelete(self, sender) :
    self.uipTransaction.Edit()
    if sender.MutationType == 'D':
      self.uipTransaction.TotalDebit -= sender.Ekuivalen
    else: # MutationType == 'C'
      self.uipTransaction.TotalCredit -= sender.Ekuivalen
    self.uipTransaction.Post()
    
  def ItemAfterPost(self, sender) :
    self.IdxCounter += 1
    self.uipTransaction.Edit()
    Idx = sender.ItemIdx

    if self.AmountList.has_key(Idx):
      jmBefore, amtBefore = self.AmountList[Idx]
      if jmBefore == 'D': self.uipTransaction.TotalDebit -= amtBefore
      else: self.uipTransaction.TotalCredit -= amtBefore

    self.AmountList[Idx] = sender.MutationType, sender.Ekuivalen

    if sender.MutationType == 'D':
      self.uipTransaction.TotalDebit += sender.Ekuivalen
    else: # MutationType == 'C'
      self.uipTransaction.TotalCredit += sender.Ekuivalen

    self.uipTransaction.Post()

  def bCancelTransaction(self, sender):
    if self.app.ConfirmDialog('Yakin batalkan transaksi ?'):
      sender.ExitAction = 1
    else:
      sender.ExitAction = 0

  def bSimpanClick(self, sender):
    if self.Simpan(1):
      self.ClearData()
    #-- if

  def bSimpanCloseClick(self, sender):
    if self.Simpan(2):
      sender.ExitAction = 1
        
  def CheckRequired(self):
    app = self.app
    uipTran = self.uipTransaction

    if uipTran.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'

    if self.uipTransactionItem.RecordCount <= 0 :
      raise 'PERINGATAN','Detail Transaksi belum diinput'

  def Simpan(self,savemode):
    app = self.app
    uipTran = self.uipTransaction
    
    self.CheckRequired()
    
    if self.uipTransaction.TotalDebit != self.uipTransaction.TotalCredit:
      self.app.ShowMessage('Total debit tidak sama dengan total kredit!')
      return 0

    if self.app.ConfirmDialog('Yakin simpan transaksi ?'):

      self.FormObject.CommitBuffer()
      ph = self.FormObject.GetDataPacket()

      ph = self.FormObject.CallServerMethod("SimpanData", ph)
      res = ph.FirstRecord
      if res.IsErr == 1:
        self.app.ShowMessage(res.ErrMessage)
        return 0
      else:
        Message = 'Transaksi Berhasil.\nNomor Transaksi : ' + res.TransactionNo
        if res.IsErr == 2:
          Message += '\n Proses Jurnal Gagal.' + res.ErrMessage

        self.app.ShowMessage(Message)

        if savemode == 2 :
          if self.app.ConfirmDialog('Apakah akan cetak kwitansi ?'):
            oPrint = app.GetClientClass('PrintLib','PrintLib')()
            #app.ShowMessage("Masukkan kertas ke printer untuk cetak kwitansi")
            oPrint.doProcessByStreamName(app,ph.packet,res.StreamName)
        self.DefaultValues['ActualDate'] = uipTran.ActualDate
        return 1

    #-- if
