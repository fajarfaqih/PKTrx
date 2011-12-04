KodeTransaksi = ['KK','KM']

DefaultItems = [ 'Inputer',
                 'BranchCode',
                 'TransactionDate',
                 'FloatTransactionDate',
                 #'LBatch.BatchId',
                 #'LBatch.BatchNo',
                 #'LBatch.Description',
                 'ActualDate',
                 'LCashAccount.AccountNo',
                 'LCashAccount.AccountName',
                 'TransactionNo',
                 'ShowMode',
                 'Amount',
                 'PaidTo',
                 'FundEntity',
                 ]


class fInvestmentReturn :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.fSearchEmployee = None
    self.fSearchBudget = None
    self.DefaultValues = {}

  # --- PRIVATE METHOD ---
  def Show(self , mode = 1):
    self.uipTransaction.Edit()
    self.uipTransaction.ShowMode = mode
    if mode == 1 :
      self.SaveDefaultValues()
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

  def SearchInvestmentClick(self,sender):
    if self.fSearchEmployee == None:
      formname = 'Transaksi/fSearchInvestment'
      form = self.app.CreateForm(formname,formname,0,None,None)
      self.fSearchEmployee = form
    else:
      form = self.fSearchEmployee
    # end if

    if form.ShowData():
      uipTran = self.uipTransaction
      uipTran.Edit()
      if form.mpInvestment.ActivePageIndex == 0 :
        uipInvest = form.uipInvestmentNE
        uipTran.InvesteeName = uipInvest.GetFieldValue('LInvestee.InvesteeName')
        uipTran.InvesteeId = uipInvest.GetFieldValue('LInvestee.InvesteeId')
        uipTran.InvestmentAmount = uipInvest.InvestmentAmount
        uipTran.InvestmentAccountNo = uipInvest.AccountNo
        uipTran.FundEntity = uipInvest.FundEntity
      else:
        uipInvest = form.uipInvestmentE
        uipTran.InvesteeName = uipInvest.GetFieldValue('LEmployee.EmployeeName')
        uipTran.InvesteeId = uipInvest.GetFieldValue('LEmployee.EmployeeId')
        uipTran.InvestmentAmount = uipInvest.InvestmentAmount
        uipTran.InvestmentAccountNo = uipInvest.AccountNo
        uipTran.FundEntity = uipInvest.FundEntity
      # end if
    
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

  def bSimpanClick(self, sender):
    if self.SimpanData() :
      if self.uipTransaction.ShowMode == 1 :
        # insert mode
        self.ClearData()
      else:
        # edit mode
        sender.ExitAction = 1
      # end if

  def CheckRequired(self):
    uipTran = self.uipTransaction

    if uipTran.InvestmentAccountNo in [0, None] :
      raise 'PERINGATAN','Data Investasi Belum Diinputkan'
      
    if uipTran.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'

    if uipTran.GetFieldValue('LCashAccount.AccountNo') in ['', None] :
      raise 'PERINGATAN','Kas / Bank Belum diinputkan'

    if ((uipTran.Amount or 0.0) <= 0.0) and ((uipTran.Share or 0.0) <= 0.0) :
      raise 'PERINGATAN','Nilai Pokok atau Bagi Hasil tidak boleh <= 0.0 '


  def SimpanData(self):
    app = self.app
    uipTran = self.uipTransaction

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

        self.DefaultValues['ActualDate'] = uipTran.ActualDate
        
        return 1
    #-- if
