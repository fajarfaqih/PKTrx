KodeTransaksi = ['KK','KM']

class fFixedAssetNew :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.fSearchEmployee = None
    self.fSearchBudget = None
    self.fSearchDonor = None
    
  def AmountOnExit(self,sender):
    self.SetTotalAmount()

  def QtyOnExit(self,sender):
    self.SetTotalAmount()
    
  def AssetTypeOnChange(self,sender):
    self.pTransaction_LProduct.Enabled = sender.ItemIndex == 0
    if sender.ItemIndex == 1 :
      uipTran = self.uipTransaction
      uipTran.Edit()
      uipTran.SetFieldValue('LProduct.ProductCode','')
      uipTran.SetFieldValue('LProduct.ProductName','')
    
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

  def SourceAssetTypeChange(self,sender):
    self.SetSourceTypeVisible(sender.ItemIndex)
    
  def PaymentTypeOnChange(self,sender):
    colors = {0:-2147483624 , 1:16777215}
    self.pPaymentInfo_CashAdvance.Enabled = sender.ItemIndex == 1
    self.pPaymentInfo_CashAdvance.Color= colors[sender.ItemIndex]
    if sender.ItemIndex == 0 :
      self.SetCashAdvance()

  def bCariDonorClick(self,sender):
    self.CariDonor()

  # --- PRIVATE METHOD ------
  def Show(self , mode = 1):
    self.uipTransaction.Edit()
    self.uipTransaction.ShowMode = mode
    self.InitValues()

    return self.FormContainer.Show()

  def InitValues(self):
    PageIndex = {'B' : 0 , 'D' : 1 }
    uipTran = self.uipTransaction
    uipTran.Edit()

    if uipTran.ShowMode == 1 : # Insert Mode
      uipTran.CashAdvance = 0.0
      uipTran.Amount = 0.0
      uipTran.AssetType = 'T'
      uipTran.PaymentType = 'T'
      uipTran.Qty = 1
      uipTran.FundEntity = 4
      uipTran.SourceAssetType = 'B'
      self.SetSourceTypeVisible(PageIndex[uipTran.SourceAssetType])
      
    else: # Edit Mode
      self.SetSourceTypeVisible(PageIndex[uipTran.SourceAssetType or 'B'])
      self.AssetTypeOnChange(self.pTransaction_AssetType)
    # end if.else
      
  def SetSourceTypeVisible(self, ItemIndex):
    self.mpSourceInfo.GetPage(0).TabVisible = (ItemIndex == 0)
    self.mpSourceInfo.GetPage(1).TabVisible = (ItemIndex == 1)
  
  def SetCashAdvance(self):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.CashAdvance = uipTran.Qty * uipTran.Amount

  def CariDonor(self):
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
      uipTran.PhoneNumber = fSearch.PhoneNumber
      uipTran.Address = fSearch.Address
      uipTran.DonorType = fSearch.DonorType
      uipTran.SetFieldValue('LMarketer.MarketerId',fSearch.MarketerId)
      uipTran.SetFieldValue('LMarketer.Full_Name',fSearch.MarketerName)
      self.DonorNo = uipTran.DonorNo
      self.pDonationInfo_edAddress.Text = str(fSearch.Address)

  def CheckRequired(self):
    app = self.app
    uipTran = self.uipTransaction
    
    self.FormObject.CommitBuffer()

    if uipTran.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'
      
    if uipTran.GetFieldValue('LAssetCategory.AssetCategoryCode') in ['',None] :
      raise 'PERINGATAN','Kategori Aset belum dipilih'

    if (uipTran.AssetType == 'T') and (uipTran.GetFieldValue('LProduct.ProductCode') in ['',None]) :
      raise 'PERINGATAN','Nama Produk/Program belum dipilih'

    if uipTran.AssetName in ['',None] :
      raise 'PERINGATAN','Nama Aset Belum Diinputkan'

    if (uipTran.Amount or 0.0) <= 0.0:
      raise 'PERINGATAN','Nilai asset tidak boleh <= 0.0'

    sourceType = self.mpSourceInfo.ActivePageIndex
    # Cek Sumber Aset
    if sourceType == 0: # Pembelian
      if uipTran.GetFieldValue('LCashAccount.AccountNo') in ['',None] :
        raise 'PERINGATAN','Kas / Bank belum dipilih'

      if (uipTran.CashAdvance or 0.0) <= 0.0:
        raise 'PERINGATAN','Nilai pembayaran tidak boleh <= 0.0'

      if uipTran.PaymentType == 'T' :
        self.SetCashAdvance()

      if (uipTran.CashAdvance or 0.0) > (uipTran.Amount or 0.0):
        raise 'PERINGATAN','Nominal uang muka lebih besar daripada nilai asset'

      if (uipTran.CashAdvance == uipTran.Amount) and uipTran.PaymentType == 'D':
        uipTran.Edit()
        uipTran.PaymentType = 'T'
        
    elif sourceType == 1 : # Donasi
    
      if uipTran.DonorId in [0,None]:
        raise 'PERINGATAN','Data Donatur belum diinputkan'
        
    else :
      raise 'PERINGATAN','Sumber Aset Tidak Dikenal'


  def SetTotalAmount(self):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.TotalAmount = (uipTran.Qty or 0.0 ) * (uipTran.Amount or 0.0)
    self.SetCashAdvance()
    
  def SetSourceAssetType(self):
    uipTran = self.uipTransaction
    uipTran.Edit()

    sourceType = self.mpSourceInfo.ActivePageIndex
    if sourceType == 0:
      uipTran.SourceAssetType = 'B'
    elif sourceType == 1:
      uipTran.SourceAssetType = 'D'

  def bSimpanClick(self, sender):
    app = self.app
    self.CheckRequired()
    
    if app.ConfirmDialog('Yakin simpan transaksi ?'):
      self.SetSourceAssetType()
      
      self.FormObject.CommitBuffer()

      ph = self.FormObject.GetDataPacket()

      ph = self.FormObject.CallServerMethod("SimpanData", ph)
      res = ph.FirstRecord
      if res.IsErr == 1:
        app.ShowMessage(res.ErrMessage)
        return 0
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
