KodeTransaksi = ['KK','KM']

class fCARAsset :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.fSearchEmployee = None
    self.fSearchBudget = None

  def GetData(self,editmode=0,data=None):
    uipData = self.uipData
    uipData.Edit()
    if editmode :
      uipData.AssetType = data.AssetType
      uipData.SetFieldValue('LAssetCategory.AssetCategoryCode',data.AssetCatCode)
      uipData.SetFieldValue('LAssetCategory.AssetCategoryName',data.AssetCatName)
      uipData.SetFieldValue('LAssetCategory.AssetCategoryId',data.AssetCatId)
      if data.AssetType == 'T' :
        uipData.SetFieldValue('LProduct.ProductCode',data.AssetProductAccountNo)
        uipData.SetFieldValue('LProduct.ProductName',data.AssetProductAccountName)

      uipData.AssetName = data.AssetName
      uipData.Description = data.Description
      uipData.BudgetCode = data.BudgetCode
      uipData.BudgetOwner = data.BudgetOwner

      uipData.PaymentType = data.AssetPaymentType
      uipData.Amount = data.AssetAmount
      uipData.Qty = data.AssetQty
      uipData.TotalAmount = uipData.Amount * uipData.Qty
      uipData.PaymentAmount = data.Amount
      
    else :
      uipData.SetFieldValue('LAssetCategory.AssetCategoryCode','')
      uipData.SetFieldValue('LAssetCategory.AssetCategoryName','')
      uipData.SetFieldValue('LAssetCategory.AssetCategoryId',0)
      uipData.SetFieldValue('LProduct.ProductCode','')
      uipData.SetFieldValue('LProduct.ProductName','')
      
      uipData.Description = ''
      uipData.BudgetCode = ''
      uipData.BudgetOwner = ''
      uipData.AssetName = ''
      
      uipData.AssetType = 'T'
      uipData.PaymentType = 'T'
      uipData.Amount = 0.0
      uipData.Qty = 1
      uipData.TotalAmount = 0.0
      uipData.PaymentAmount = 0.0
    # end if

    st = self.FormContainer.Show()
    if st == 1 : return 1
    return 0

  def AmountOnExit(self,sender):
    self.SetTotalAmount()

  def QtyOnExit(self,sender):
    self.SetTotalAmount()

  def AssetTypeOnChange(self,sender):
    self.pTransaction_LProduct.Enabled = sender.ItemIndex == 0
    if sender.ItemIndex == 1 :
      uipData = self.uipData
      uipData.Edit()
      uipData.SetFieldValue('LProduct.ProductCode','')
      uipData.SetFieldValue('LProduct.ProductName','')
      uipData.SetFieldValue('LAssetCategory.AssetCategoryCode','')
      uipData.SetFieldValue('LAssetCategory.AssetCategoryName','')
      uipData.SetFieldValue('LAssetCategory.AssetCategoryId',0)

  def bSearchBudgetClick(self, sender):
    uipTran = self.uipData
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

  def PaymentTypeOnChange(self,sender):
    colors = {0:-2147483624 , 1:16777215}
    self.pTransaction_PaymentAmount.Enabled = sender.ItemIndex == 1
    self.pTransaction_PaymentAmount.Color= colors[sender.ItemIndex]
    if sender.ItemIndex == 0 :
      self.SetPaymentAmount()


  # --- PRIVATE METHOD ------
  def Show(self , mode = 1):
    self.InitValues()
    self.uipData.ShowMode = mode

    return self.FormContainer.Show()

  def InitValues(self):
    uipTran = self.uipData
    uipTran.Edit()
    uipTran.CashAdvance = 0.0
    uipTran.Amount = 0.0
    uipTran.AssetType = 'T'
    uipTran.PaymentType = 'T'
    uipTran.Qty = 1

  def SetPaymentAmount(self):
    uipTran = self.uipData
    uipTran.Edit()
    uipTran.PaymentAmount = uipTran.Qty * uipTran.Amount

  def CheckInput(self):
    app = self.app
    uipTran = self.uipData

    self.FormObject.CommitBuffer()

    if (uipTran.Amount or 0.0) < 0.0:
      raise 'PERINGATAN','Nilai asset belum diinputkan'

    if uipTran.PaymentType == 'T' :
      self.SetPaymentAmount()

    if (uipTran.PaymentAmount or 0.0) > (uipTran.Amount or 0.0):
      raise 'PERINGATAN','Nominal uang muka lebih besar daripada nilai asset'

  def SetTotalAmount(self):
    uipTran = self.uipData
    uipTran.Edit()
    uipTran.TotalAmount = (uipTran.Qty or 0.0 ) * (uipTran.Amount or 0.0)

  def CheckRequiredData(self):
    uipData = self.uipData

    if uipData.GetFieldValue('LAssetCategory.AssetCategoryCode') in ['',None] :
      raise 'PERINGATAN','Kategori Aset belum dipilih'

    if (uipData.AssetType == 'T') and (uipData.GetFieldValue('LProduct.ProductCode') in ['',None]) :
      raise 'PERINGATAN','Nama Produk/Program belum dipilih'

    if uipData.AssetName in ['',None] :
      raise 'PERINGATAN','Nama Aset Belum Diinputkan'

    if (uipData.Amount or 0.0) <= 0.0:
      raise 'PERINGATAN','Nilai asset tidak boleh <= 0.0'

    if uipData.PaymentType == 'T' :
      uipData.PaymentAmount = uipData.Amount

    if (uipData.PaymentAmount or 0.0) <= 0.0:
      raise 'PERINGATAN','Nilai pembayaran tidak boleh <= 0.0'

    if (uipData.PaymentAmount or 0.0) > (uipData.Amount or 0.0):
      raise 'PERINGATAN','Nominal pembayaran / angsuran awal lebih besar daripada nilai asset'

  def bSaveClick(self,sender):
    self.CheckRequiredData()
    sender.ExitAction = 1
