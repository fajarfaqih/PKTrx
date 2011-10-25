PI_NONE   = -1
PI_BANK   = 0
PI_BRANCH = 1
PI_PETTY  = 2

class fCashAccountReport:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication

  def DisplayPage(self, PageIdx) :
    for i in range(self.mpAccount.PageCount):
      self.mpAccount.GetPage(i).TabVisible = i == PageIdx

    self.mpAccount.ActivePageIndex = PageIdx

  def Show(self):
    self.DisplayPage(PI_NONE)
    return self.FormContainer.Show()

  def AccountAfterLookup (self, sender, linkui):
    accountType = self.uipCashAccount.GetFieldValue('LCashAccount.CashAccountType')

    ph = self.app.CreateValues(['AccountNo',
      self.uipCashAccount.GetFieldValue('LCashAccount.AccountNo')])

    ph = self.FormObject.CallServerMethod("SearchCashAccount", ph)
    res = ph.FirstRecord

    self.uipCashAccount.BranchCode = res.BranchCode
    self.uipCashAccount.CurrencyCode = res.CurrencyCode
    self.uipCashAccount.Balance = res.Balance
    
    if accountType == 'A':
      self.uipCashAccount.BankAccountNo = res.BankAccountNo
      self.uipCashAccount.BankName = res.BankName
      self.DisplayPage(PI_BANK)
    elif accountType == 'R':
      self.DisplayPage(PI_BRANCH)
    elif accountType == 'P':
      self.uipCashAccount.UserName = res.UserName
      self.DisplayPage(PI_PETTY)

  def bViewHistClick (self, sender):
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['AccountNo', self.uipCashAccount.GetFieldValue('LCashAccount.AccountNo')],
        ['BeginDate', self.uipCashAccount.BeginDate],
        ['EndDate', self.uipCashAccount.EndDate]
      )
    )

    self.uipCashAccount.BeginningBalance = ph.FirstRecord.BeginningBalance
    uipTran = self.uipTransaction
    uipTran.ClearData()

    ds = ph.packet.histori
    i = 0
    while i < ds.RecordCount:
      rec = ds.GetRecord(i)
      uipTran.Append()

      uipTran.TransactionItemId = rec.TransactionItemId
      uipTran.TransactionDate   = rec.TransactionDate
      uipTran.TransactionCode   = rec.TransactionCode
      uipTran.MutationType      = rec.MutationType
      uipTran.Amount            = rec.Amount
      uipTran.ReferenceNo       = rec.ReferenceNo
      uipTran.Description       = rec.Description
      uipTran.Inputer           = rec.Inputer

      i += 1
    # end of while

    uipTran.First()

