KodeTransaksi = ['KK','KM']

DefaultItems = [ 'Inputer',
                 'BranchCode',
                 'TransactionDate',
                 'FloatTransactionDate',
                 #'LBatch.BatchId',
                 #'LBatch.BatchNo',
                 #'LBatch.Description',
                 'LCashAccount.AccountNo',
                 'LCashAccount.AccountName',
                 'TransactionNo',
                 'ShowMode',
                 'Amount',
                 'ReceivedFrom',
                 'FundEntity',
                 'PeriodId',
                 'ActualDate'
                 ]


class fCashAdvance :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.fSearchEmployee = None
    self.fSearchBudget = None
    self.fSearchRAK = None
    self.fSelectProduct = None
    self.DefaultValues = {}

  # --- PRIVATE METHOD ---
  def Show(self , mode = 1):
    uipTran = self.uipTransaction

    uipTran.Edit()
    uipTran.ShowMode = mode
    
    if mode == 1 : # Insert Mode
      uipTran.FundEntity = 4
      self.SaveDefaultValues()
    else: # Edit Mode
      self.pTransaction2_Rate.Enabled = (uipTran.CurrencyCode != '000')
      
    return self.FormContainer.Show()


  def SaveDefaultValues(self):
    uipTran = self.uipTransaction
    for item in DefaultItems :
      self.DefaultValues[item] = uipTran.GetFieldValue(item)

  def ClearData(self):
    self.uipTransaction.ClearData()

    uipTran = self.uipTransaction
    uipTran.Edit()
    for item in DefaultItems :
      uipTran.SetFieldValue(item,self.DefaultValues[item])

    #self.pTransaction_LBatch.SetFocus()
    self.pTransaction_ActualDate.SetFocus()

  # --- FORM EVENT ---
  def BatchAfterLookup(self, sender, linkui):
    uipTran = self.uipTransaction
    uipTran.Edit()
    self.DefaultValues['LBatch.BatchId'] = uipTran.GetFieldValue('LBatch.BatchId')
    self.DefaultValues['LBatch.BatchNo'] = uipTran.GetFieldValue('LBatch.BatchNo')
    self.DefaultValues['LBatch.Description'] = uipTran.GetFieldValue('LBatch.Description')

  def EmployeeAfterLookup (self, sender, linkui):
    self.uipTransaction.EmployeeName = self.uipTransaction.GetFieldValue('LEmployee.Nama_Lengkap')

  def CashAccountAfterLookup(self, sender, linkui):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.CurrencyCode = uipTran.GetFieldValue('LCashAccount.CurrencyCode')
    uipTran.CurrencyName = uipTran.GetFieldValue('LCashAccount.LCurrency.Short_Name')
    uipTran.Rate = uipTran.GetFieldValue('LCashAccount.LCurrency.Kurs_Tengah_BI')

    self.pTransaction2_Rate.Enabled = (uipTran.CurrencyCode != '000')
    
  def RateOnExit(self,sender):
    self.SetEkuivalenAmount()

  def AmountOnExit(self,sender):
    self.SetEkuivalenAmount()
    
  def SearchEmployeeClick(self,sender):
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
    
  def bSearchBudgetClick(self, sender):
    uipTran = self.uipTransaction
    if self.fSearchBudget == None:
      #formname = 'Transaksi/fSelectBudgetYear'
      formname = 'Transaksi/fSelectBudgetCode'
      form = self.app.CreateForm(formname,formname,0,None,None)
      self.fSearchBudget = form
    else:
      form = self.fSearchBudget
    # end if
    
    ActualDate = self.uipTransaction.ActualDate or 0
    if ActualDate == 0 :
      raise 'Peringatan','Tanggal transaksi belum diinput. Silahkan input tanggal transaksi lebih dahulu'

    if form.GetBudget(ActualDate) == 1:
      uipTran.Edit()
      uipTran.BudgetCode = form.BudgetCode
      uipTran.BudgetOwner = form.BudgetOwner
      uipTran.BudgetId = form.BudgetId
    # end if

  def bSearchProductClick(self,sender):
    uipTran = self.uipTransaction
    if self.fSelectProduct == None:
      fProduct = self.app.CreateForm('Transaksi/fSelectProduct', 'Transaksi/fSelectProduct', 0, None, None)
      self.fSelectProduct = fProduct
    else:
      fProduct = self.fSelectProduct
    # end if

    branchCode = uipTran.BranchCode
    if fProduct.GetProduct(branchCode) == 1:
      uipTran.Edit()
      uipTran.ProductAccountNo = fProduct.AccountNo
      uipTran.ProductAccountName = fProduct.ProductName
      #self.uipTransactionItem.ProductId = productId
      #self.uipTransactionItem.FundEntityCollection = MAPEntity[fProduct.FundCategory or 'I']
      #self.uipTransactionItem.PercentageOfAmil = fProduct.PercentageOfAmilFunds

    return 1
    
  def bSearchRAKClick(self,sender):
    uipTran = self.uipTransaction
    if self.fSearchRAK == None:
      formname = 'Transaksi/fSelectDistributionTransfer'
      form = self.app.CreateForm(formname,formname,0,None,None)
      self.fSearchRAK = form
    else:
      form = self.fSearchRAK
    # end if

    if form.GetTransaction('IN'):
      uipTran.Edit()
      uipDist = form.uipDistributionList
      uipTran.DistTransactionNo = uipDist.TransactionNo
      uipTran.DistSourceBranchCode = uipDist.BranchCodeSource
      uipTran.DistSourceBranchName = uipDist.BranchNameSource
      uipTran.DistAmount = uipDist.Amount
      uipTran.DistBalance = uipDist.Balance
      uipTran.DistributionId = uipDist.DistributionId
    # end if
    
  def bSimpanClick(self, sender):
    if self.SimpanData() :
      if self.uipTransaction.ShowMode == 1 :
        # insert mode
        self.ClearData()
      else:
        # edit mode
        sender.ExitAction = 1
      # end if

  def SetEkuivalenAmount(self):
    uipTran = self.uipTransaction
    uipTran.AmountEkuivalen = (uipTran.Amount or 0.0) * (uipTran.Rate or 1.0)
    
  def CheckRequired(self):
    uipTran  = self.uipTransaction

    if uipTran.ActualDate in [0, None] :
      self.app.ShowMessage('Tanggal Transaksi belum diinputkan')
      return 0

    if uipTran.GetFieldValue('LCashAccount.AccountNo') in ['', None] :
      self.app.ShowMessage('Kas / Bank Belum diinputkan')
      return 0

    if uipTran.EmployeeId in [0,None] :
      self.app.ShowMessage('Nama Karyawan Belum diinputkan')
      return 0

    if (uipTran.Amount or 0.0) <= 0.0 :
      self.app.ShowMessage('Nilai Transaksi tidak boleh <= 0.0 ')
      return 0

    return 1

  def SimpanData(self):
    app = self.app
    uipTran = self.uipTransaction

    if not self.CheckRequired(): return 0
    
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
        self.DefaultValues['ActualDate'] = uipTran.ActualDate
        return 1
    #-- if
