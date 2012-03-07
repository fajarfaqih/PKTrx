KodeTransaksi = ['KK','KM']

DefaultItems = [ 'Inputer',
                 'BranchCode',
                 'TransactionDate',
                 'FloatTransactionDate',
                 'ActualDate',
                 'LCashAccount.AccountNo',
                 'LCashAccount.AccountName',
                 'TransactionNo',
                 'ShowMode',
                 'Amount',
                 'ReceivedFrom',
                 'FundEntity',
                 ]


class fInvestment :
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
      self.uipTransaction.FundEntity = 4
      self.SaveDefaultValues()
    else:
      self.pInvestment_bSearchEmployee.Enabled = 0
      
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

    self.pTransaction_ActualDate.SetFocus()

  # --- FORM EVENT ---
  def EmployeeAfterLookup (self, sender, linkui):
    self.uipTransaction.EmployeeName = self.uipTransaction.GetFieldValue('LEmployee.Nama_Lengkap')

  def fSearchInvestee(self,sender):
    if self.fSearchEmployee == None:
      formname = 'Transaksi/fSearchInvestee'
      form = self.app.CreateForm(formname,formname,0,None,None)
      self.fSearchEmployee = form
    else:
      form = self.fSearchEmployee
    # end if

    if form.ShowData():
      uipTran = self.uipTransaction
      uipTran.Edit()
      if form.mpInvestee.ActivePageIndex == 0 :
        uipTran.InvesteeName = form.uipInvestee.InvesteeName
        uipTran.InvesteeId = form.uipInvestee.InvesteeId
        uipTran.InvesteeCategory = 1
      else:
        uipTran.InvesteeName = form.uipEmployee.EmployeeName
        uipTran.InvesteeId = form.uipEmployee.EmployeeId
        uipTran.InvesteeCategory = 2
      # end if
    # end if
    
  def bSearchBudgetClick(self, sender):
    uipTran = self.uipTransaction
    if self.fSearchBudget == None:
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
    
    if uipTran.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'
      
    if uipTran.GetFieldValue('LCashAccount.AccountNo') in ['', None] :
      raise 'PERINGATAN','Kas / Bank Belum diinputkan'

    if (uipTran.Amount or 0.0) <= 0.0 :
      raise 'PERINGATAN','Nilai Transaksi tidak boleh <= 0.0 '

    if uipTran.GetFieldValue('LInvestmentCategory.InvestmentCatCode') in ['', None] :
      raise 'PERINGATAN','Jenis Investasi Belum diinputkan'
      
    if uipTran.InvesteeId in [0, None] :
      raise 'PERINGATAN','Nama Investee Belum diinputkan'

    if uipTran.StartDate in [0, None] :
      raise 'PERINGATAN','Tanggal Mulai Investasi belum diinputkan'
      
    if uipTran.LifeTime in [0, None] :
      raise 'PERINGATAN','Jangka Waktu Investasi belum diinputkan'

    if uipTran.Nisbah in [0, None] :
      raise 'PERINGATAN','Nisbah Investasi belum diinputkan'
      
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
