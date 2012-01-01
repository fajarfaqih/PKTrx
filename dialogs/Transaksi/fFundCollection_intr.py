# GLOBALs
MAPEntity = {'Z': 1, 'I': 2, 'W': 3}

DefaultItems = [ 'Inputer',
                 'BranchCode',
                 'TransactionDate',
                 'FloatTransactionDate',
                 'CurrencyCode',
                 'Rate',
                 'TotalAmount',
                 'CashType',
                 #'LBatch.BatchId',
                 #'LBatch.BatchNo',
                 #'LBatch.Description',
                 'LProductBranch.Kode_Cabang',
                 'LProductBranch.Nama_Cabang',
                 'LCurrency.Currency_Code',
                 'LCurrency.Full_Name',
                 'LCurrency.Kurs_Tengah_BI',
                 'LValuta.Currency_Code',
                 'LValuta.Full_Name',
                 'LValuta.Kurs_Tengah_BI',
                 'LBank.AccountNo',
                 'LBank.BankName',
                 'LBank.CurrencyCode',
                 'PeriodId',
                 'LSponsor.SponsorId',
                 'LVolunteer.VolunteerId',
                 'TransactionNo',
                 'ShowMode',
                 'PaidTo',
                 'ActualDate',
                 ]

class fFundCollection :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.form = formObj
    self.fSelectProduct = None
    self.fSearchDonor = None
    self.DefaultValues = {}
    self.IdxCounter = 0

    
  def InitValues(self):
    if self.uipTransaction.ShowMode == 1 : # input mode
      self.DonorNo = self.uipDonor.DonorNo
      self.AmountList = {}
      self.IdxCounter = 1
    else: # edit mode
      self.DonorNo = self.uipDonor.DonorNo
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
      
      # Hitung Ulang Total Penghimpunan
      uipTran.Edit()
      uipTran.TotalAmount = TotalAmount
    # end if else
    self.CheckRateEnabled()
      
  def SaveDefaultValues(self):
    uipTran = self.uipTransaction
    for item in DefaultItems :
      self.DefaultValues[item] = uipTran.GetFieldValue(item)

  def ClearData(self):
    self.InitValues()
    self.uipDonor.ClearData()
    self.uipTransaction.ClearData()
    self.uipTransactionItem.ClearData()

    uipTran = self.uipTransaction
    uipTran.Edit()
    for item in DefaultItems :
      uipTran.SetFieldValue(item,self.DefaultValues[item])

    self.CariDonor()
    #self.pBatch_LBatch.SetFocus()
    self.pBatch_ActualDate.SetFocus()

  # mode
  # 1 : input mode
  # 2 : edit mode
  def Show(self,mode=1):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.ShowMode = mode
    self.InitValues()
    self.DonorNo = self.uipDonor.DonorNo
    if mode == 2: # Edit Mode
      #self.pBatch_LBatch.Enabled = 0
      # Set Save button hidden
      self.pAction_bSave.Visible = 0
      
      # Move button position
      self.pAction_bCancel.Left = self.pAction_bSimpanClose.Left
      self.pAction_bSimpanClose.Left = self.pAction_bSave.Left
      
      PageIndex = {'C' : 0 , 'K' : 0 ,'B' : 1 , 'A':2}

      self.mpBayar.ActivePageIndex = PageIndex[uipTran.PaymentType]

    else: # Insert Mode
      self.CariDonor()
      self.SaveDefaultValues()
    # end if
    
    #self.pDonor_edAddress.Text = str(self.uipDonor.Address)
    return self.FormContainer.Show()

  def bCariDonorClick(self,sender):
    self.CariDonor()

  def IdDonorOnExit(self,sender):
    uipDonor = self.uipDonor
    DonorNo = uipDonor.DonorNo or ''

    if ( DonorNo == '' or
         ( DonorNo not in [None,''] and
           DonorNo == self.DonorNo)
       ) :
      return


    rph = self.form.CallServerMethod(
           'GetDonorDataByNo',
           self.app.CreateValues(['DonorNo',DonorNo])
           )


    uipDonor.Edit()

    rec = rph.FirstRecord
    if rec.Is_Err :
      uipDonor.DonorName = ''
      uipDonor.PhoneNumber = ''
      uipDonor.Address = ''
      self.pDonor_edAddress.Text = ''
      self.DonorNo = None
      uipDonor.SetFieldValue('LMarketer.MarketerId',0)
      uipDonor.SetFieldValue('LMarketer.Full_Name','')

      raise 'PERINGATAN',rec.Err_Message
    
    uipDonor.DonorId = rec.DonorId
    uipDonor.DonorName = rec.DonorName
    uipDonor.PhoneNumber = rec.PhoneNumber
    uipDonor.Address = rec.Address
    uipDonor.DonorType = rec.DonorType
    self.pDonor_edAddress.Text = str(rec.Address)
    self.DonorNo = uipDonor.DonorNo
    uipDonor.SetFieldValue('LMarketer.MarketerId',rec.MarketerId)
    uipDonor.SetFieldValue('LMarketer.Full_Name',rec.MarketerName)

  def CariDonor(self):
    if self.fSearchDonor == None :
      fSearch = self.app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
      self.fSearchDonor = fSearch
    else :
      fSearch = self.fSearchDonor

    if fSearch.GetDonorData():
      uipDonor = self.uipDonor
      uipDonor.Edit()

      uipDonor.DonorId = fSearch.DonorIntId
      uipDonor.DonorNo = fSearch.DonorNo
      uipDonor.DonorName = fSearch.DonorName
      uipDonor.PhoneNumber = fSearch.PhoneNumber
      uipDonor.Address = fSearch.Address
      uipDonor.DonorType = fSearch.DonorType
      self.DonorNo = uipDonor.DonorNo
      self.pDonor_edAddress.Text = str(fSearch.Address)
      uipDonor.SetFieldValue('LMarketer.MarketerId',fSearch.MarketerId)
      uipDonor.SetFieldValue('LMarketer.Full_Name',fSearch.MarketerName)
      
  def ProductBeforeLookup(self, sender, linkui):
    if self.fSelectProduct == None:
      fData = self.app.CreateForm('Transaksi/fSelectProduct', 'Transaksi/fSelectProduct', 0, None, None)
      self.fSelectProduct = fData
    else:
      fData = self.fSelectProduct
    branchCode = self.uipTransaction.BranchCode #GetFieldValue('LProductBranch.Kode_Cabang')
    if fData.GetProduct(branchCode) == 1:
      productId = fData.ProductId
      productName = fData.ProductName

      self.uipTransactionItem.Edit()
      self.uipTransactionItem.SetFieldValue('LProduct.ProductId', productId)
      self.uipTransactionItem.SetFieldValue('LProduct.ProductName', productName)
      self.uipTransactionItem.FundEntity = MAPEntity[fData.FundCategory or 'I']
      self.uipTransactionItem.PercentageOfAmil = fData.PercentageOfAmilFunds
      self.uipTransactionItem.AccountNo = fData.AccountNo
      self.uipTransactionItem.Description = productName

    return 1

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
    self.CheckRateEnabled()

    
  def ItemNewRecord (self, sender):
    sender.ItemIdx = self.IdxCounter
    sender.Amount = 0.0
    #sender.Rate   = 1.0
    #sender.Ekuivalen = 0.0
    #sender.SetFieldValue('LCurrency.Currency_Code', '000')
    #sender.SetFieldValue('LCurrency.Short_Name', 'IDR')

  def ItemBeforePost(self, sender) :
    aProductId = sender.GetFieldValue('LProduct.ProductId')
    if aProductId == None or aProductId == 0:
      raise 'Produk', 'Produk belum dipilih'
      #self.app.ShowMessage('Produk belum dipilih')
      #sender.Cancel()
      
    if sender.Amount <= 0.0 :
      raise 'Nilai Transaksi', 'Nilai transaksi tidak boleh negatif atau 0.0'

    #sender.Ekuivalen = sender.Amount * sender.Rate

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
    uipDonor = self.uipDonor
    uipTran  = self.uipTransaction
    #if uipTran.GetFieldValue('LBatch.BatchId') == None:
    #  self.app.ShowMessage('Batch belum dipilih')
    #  return 0

    if uipDonor.DonorId in [0,None]:
      self.app.ShowMessage('Data Donatur belum diinputkan')
      return 0
      
    if uipTran.ActualDate in [0, None] :
      self.app.ShowMessage('Tanggal Transaksi belum diinputkan')
      return 0

    if self.uipTransactionItem.RecordCount <= 0 :
      self.app.ShowMessage('Detail Transaksi belum diinput')
      return 0

    ReferenceNo = uipTran.ReferenceNo or ''
    pType = self.mpBayar.ActivePageIndex
    if (ReferenceNo == '' and pType != 1 ) :
      self.app.ShowMessage('No. Referensi/FSZ Belum Diinput')
      return 0
      
    return 1

  def CheckRateEnabled(self):
    uipTran = self.uipTransaction
    self.pCashTransaction_RateCash.Enabled = uipTran.GetFieldValue('LCurrency.Currency_Code') != '000'
    self.pBankTransaction_RateBank.Enabled = uipTran.GetFieldValue('LBank.CurrencyCode') != '000'
    self.pAssetTransaction_RateAsset.Enabled = uipTran.GetFieldValue('LValuta.Currency_Code') != '000'
    
  def CurrencyAfterLookup(self,sender,linkui):
    uipTransaction = self.uipTransaction
    if uipTransaction.GetFieldValue('LCurrency.Currency_Code') != None :
       uipTransaction.Edit()
       uipTransaction.Rate = uipTransaction.GetFieldValue('LCurrency.Kurs_Tengah_BI')
    self.CheckRateEnabled()
    
  def ValutaAfterLookup(self, sender, linkui):
    uipTransaction = self.uipTransaction
    if uipTransaction.GetFieldValue('LValuta.Currency_Code') != None :
       uipTransaction.Edit()
       uipTransaction.Rate = uipTransaction.GetFieldValue('LValuta.Kurs_Tengah_BI')
    self.CheckRateEnabled()
    
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

    if app.ConfirmDialog('Yakin simpan transaksi ?'):
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
        app.ShowMessage(res.ErrMessage)
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

        #if savemode == 1 :
        #  self.DefaultValues['TransactionNo'] = res.NewTransactionNo
        self.DefaultValues['ActualDate'] = uipTran.ActualDate
      return 1
    #-- if
    return 0
    
