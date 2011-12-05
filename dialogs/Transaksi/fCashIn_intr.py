# GLOBALs
DefaultItems = [ 'Inputer',
                 'BranchCode',
                 'TransactionDate',
                 'FloatTransactionDate',
                 'Rate',
                 'TotalAmount',
                 'CashType',
                 #'LBatch.BatchId',
                 #'LBatch.BatchNo',
                 'ActualDate',
                 'LValuta.Currency_Code',
                 'LValuta.Full_Name',
                 'LValuta.Kurs_Tengah_BI',
                 'PeriodId',
                 'TransactionNo',
                 'PaidTo',
                 'ShowMode',
                 ]

class fCashIn :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.fSelectAccount = None
    self.fSelectBudget = None
    self.Budgets = {}
    self.DefaultValues = {}

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
      self.IdxCounter = 1
      self.AmountList = {}
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

  def Show(self,mode = 1 ):
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

  def LCurrencyCashAfterLookup(self,sender,linkui):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.RateCash = uipTran.GetFieldValue('LCurrencyCash.Kurs_Tengah_BI')
    uipTran.CurrencyCode = self.GetCurrencyCode()
    uipTran.Rate = self.GetRate()
    self.pCashTransaction_RateCash.enabled = (uipTran.GetFieldValue('LCurrencyCash.Currency_Code') != '000')
    
  def BankAfterLookup(self,sender,linkui):
    uipTran = self.uipTransaction
    uipTran.Edit()
    uipTran.RateBank = uipTran.GetFieldValue('LBank.LCurrency.Kurs_Tengah_BI')
    uipTran.CurrencyCode = self.GetCurrencyCode()
    uipTran.Rate = self.GetRate()
    self.pBankTransaction_RateBank.enabled = (uipTran.GetFieldValue('LBank.CurrencyCode') != '000')
    
  def GetRate(self):
    dictRateByPaymentType = {
      0 : 'RateCash',
      1 : 'RateBank',
    }
    uipTran = self.uipTransaction
    return uipTran.GetFieldValue(dictRateByPaymentType[self.mpBayar.ActivePageIndex])

  def GetCurrencyCode(self):
    dictCurrCodeByPaymentType = {
      0 : 'LCurrencyCash.Currency_Code',
      1 : 'LBank.CurrencyCode',
    }
    uipTran = self.uipTransaction
    return uipTran.GetFieldValue(dictCurrCodeByPaymentType[self.mpBayar.ActivePageIndex])

  def GLAccountBeforeLookup(self,sender,linkui):
    if self.fSelectAccount == None :
      formname = 'Transaksi/fSelectAccount'
      fSelectAccount = self.app.CreateForm(formname,formname,0,None,None)
      self.fSelectAccount = fSelectAccount

    if self.fSelectAccount.GetAccount(" and NOT Account_Code llike '6%' ") == 1:
      AccountCode = self.fSelectAccount.Account_Code
      AccountName = self.fSelectAccount.Account_Name
      
      self.uipTransactionItem.Edit()
      self.uipTransactionItem.AccountCode = AccountCode
      self.uipTransactionItem.AccountName = AccountName
      self.uipTransactionItem.Description = AccountName

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

  def ItemNewRecord (self, sender):
    sender.ItemIdx = self.IdxCounter
    sender.Amount = 0.0
    #sender.Rate   = self.GetRate()
    #sender.Ekuivalen = 0.0
    #sender.SetFieldValue('LCurrency.Currency_Code', '000')
    #sender.SetFieldValue('LCurrency.Short_Name', 'IDR')

  def ItemBeforePost(self, sender) :
    AccountCode = sender.AccountCode
    if AccountCode == None or AccountCode == 0:
      raise 'Account', 'Kode Account belum dipilih'

    if sender.Amount <= 0.0 :
      raise 'Nilai Transaksi', 'Nilai transaksi tidak boleh negatif atau 0.0'

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

  def CheckRequiredGeneral(self):
    uipTran  = self.uipTransaction

    if uipTran.ActualDate in [0, None] :
      self.app.ShowMessage('Tanggal Transaksi belum diinputkan')
      return 0

    if self.uipTransactionItem.RecordCount <= 0 :
      self.app.ShowMessage('Detail Transaksi belum diinput')
      return 0
      
    return 1

  def CheckRequiredCash(self):
    if self.uipTransaction.GetFieldValue('LCurrencyCash.Currency_Code') == None:
      self.app.ShowMessage('Kode Valuta Kas belum dipilih')
      return 0
    else:
      return 1

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

  def ValutaAfterLookup(self, sender, linkui):
    uipTransaction = self.uipTransaction
    if uipTransaction.GetFieldValue('LValuta.Currency_Code') != None :
       uipTransaction.Edit()
       uipTransaction.Rate = uipTransaction.GetFieldValue('LValuta.Kurs_Tengah_BI')


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
      uipTran.CurrencyCode = self.GetCurrencyCode()
      uipTran.Rate = self.GetRate()
      
      pType = self.mpBayar.ActivePageIndex
      if pType == 0:
        self.uipTransaction.PaymentType = self.uipTransaction.CashType
        if not self.CheckRequiredCash():
          return 0
      elif pType == 1:
        self.uipTransaction.PaymentType = 'B'
        if not self.CheckRequiredBank():
          return 0
      else: #pType == 2:
        self.uipTransaction.PaymentType = 'A'
        if not self.CheckRequiredAsset():
          return 0

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

