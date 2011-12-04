KodeTransaksi = ['KK','KM']

class fFixedAssetNew :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.fSearchEmployee = None
    self.fSearchBudget = None

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

  def PaymentTypeOnChange(self,sender):
    colors = {0:-2147483624 , 1:16777215}
    self.pTransaction_CashAdvance.Enabled = sender.ItemIndex == 1
    self.pTransaction_CashAdvance.Color= colors[sender.ItemIndex]
    if sender.ItemIndex == 0 :
      self.SetCashAdvance()


  # --- PRIVATE METHOD ------
  def Show(self , mode = 1):
    self.uipTransaction.Edit()
    self.uipTransaction.ShowMode = mode
    self.InitValues()

    return self.FormContainer.Show()

  def InitValues(self):
    uipTran = self.uipTransaction
    uipTran.Edit()
    if uipTran.ShowMode == 1 :
      uipTran.CashAdvance = 0.0
      uipTran.Amount = 0.0
      uipTran.AssetType = 'T'
      uipTran.PaymentType = 'T'
      uipTran.Qty = 1
    else:
      self.AssetTypeOnChange(self.pTransaction_AssetType)
    # end if.else
      
  def SetCashAdvance(self):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.CashAdvance = uipTran.Qty * uipTran.Amount
    
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

    if uipTran.GetFieldValue('LCashAccount.AccountNo') in ['',None] :
      raise 'PERINGATAN','Kas / Bank belum dipilih'

    if (uipTran.CashAdvance or 0.0) <= 0.0:
      raise 'PERINGATAN','Nilai pembayaran tidak boleh <= 0.0'

    if uipTran.PaymentType == 'T' :
      self.SetCashAdvance()
      
    if (uipTran.CashAdvance or 0.0) > (uipTran.Amount or 0.0):
      raise 'PERINGATAN','Nominal uang muka lebih besar daripada nilai asset'

  def SetTotalAmount(self):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.TotalAmount = (uipTran.Qty or 0.0 ) * (uipTran.Amount or 0.0)
    self.SetCashAdvance()
    
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
