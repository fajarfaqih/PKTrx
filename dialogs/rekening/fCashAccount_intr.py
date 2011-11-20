PI_NONE   = -1
PI_BANK   = 0
PI_BRANCH = 1
PI_PETTY  = 2

class fCashAccount:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
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

    #self.uipCashAccount.BranchCode = res.BranchCode
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
    self.ViewHistTransaction(1)

  def bExportClick(self,sender):
    app = self.app

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename == '' : return

    self.ViewHistTransaction(2,filename)

  def ViewHistTransaction(self,mode,filename=None):
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['AccountNo', self.uipCashAccount.GetFieldValue('LCashAccount.AccountNo')],
        ['BeginDate', self.uipCashAccount.BeginDate],
        ['EndDate', self.uipCashAccount.EndDate]
      )
    )

    ds = ph.packet.histori
    if mode == 1 :
      self.uipCashAccount.BeginningBalance = ph.FirstRecord.BeginningBalance
      uipTran = self.uipTransaction
      uipTran.ClearData()

      i = 0
      while i < ds.RecordCount:
        recDetail = ds.GetRecord(i)
        uipTran.Append()

        uipTran.TransactionItemId = recDetail.TransactionItemId
        uipTran.TransactionDate   = recDetail.TransactionDate
        uipTran.TransactionCode   = recDetail.TransactionCode
        uipTran.TransactionNo   = recDetail.TransactionNo
        uipTran.MutationType      = recDetail.MutationType
        uipTran.Amount            = recDetail.Amount
        uipTran.Balance           = recDetail.Balance
        uipTran.ReferenceNo       = recDetail.ReferenceNo
        uipTran.Description       = recDetail.Description
        uipTran.Inputer           = recDetail.Inputer
        uipTran.AuthStatus        = recDetail.AuthStatus

        i += 1
      # end of while

      uipTran.First()
      
      # Set Summary
      recStatus = ph.FirstRecord
      uipCashAccount = self.uipCashAccount
      uipCashAccount.Edit()
      uipCashAccount.TotalCredit = recStatus.TotalCredit
      uipCashAccount.TotalDebet = recStatus.TotalDebet
      uipCashAccount.EndBalance = recStatus.EndBalance

    else:
      rec = ph.FirstRecord
      workbook = self.oPrint.OpenExcelTemplate(self.app,'tplHistTransCashAccount.xls')
      workbook.ActivateWorksheet('data')
      
      workbook.SetCellValue(2, 2, rec.CashAccountNo)
      workbook.SetCellValue(3, 2, rec.CashAccountName)
      workbook.SetCellValue(4, 2, rec.CashAccountBranch)
      workbook.SetCellValue(5, 2, rec.Periode)
      workbook.SetCellValue(6, 2, rec.CashAccountCurrency)
      workbook.SetCellValue(7, 2, rec.BeginningBalance)
      workbook.SetCellValue(8, 2, rec.TotalCredit)
      workbook.SetCellValue(9, 2, rec.TotalDebet)
      workbook.SetCellValue(10, 2, rec.EndBalance)

      try:
        i = 0
        while i < ds.RecordCount:
          recDetail = ds.GetRecord(i)
          row = i + 13
          workbook.SetCellValue(row, 1, str(i+1))
          workbook.SetCellValue(row, 2, recDetail.TransactionDateStr)
          workbook.SetCellValue(row, 3, recDetail.TransactionNo)
          workbook.SetCellValue(row, 4, recDetail.MutationType)
          workbook.SetCellValue(row, 5, recDetail.Amount)
          workbook.SetCellValue(row, 6, recDetail.Balance)
          workbook.SetCellValue(row, 7, recDetail.Description)
          workbook.SetCellValue(row, 8, recDetail.Inputer)
          workbook.SetCellValue(row, 9, recDetail.AuthStatus)

          i += 1
        # end of while


        workbook.SaveAs(filename)
        self.app.ShellExecuteFile(filename)
      finally:
        # close
        workbook = None

