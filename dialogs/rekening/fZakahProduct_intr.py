class fZakahProduct:

  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

  # ----- FORM EVENT
  def bViewHistClick (self, sender):
    self.ViewHistTransaction(1)

  def bExportClick(self,sender):
    app = self.app

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return

    self.ViewHistTransaction(2,filename)

  def ProgramAfterLookup(self,sender,linkUI):
    CurrencyCode = self.uipProductAccount.GetFieldValue('LCurrency.Currency_Code') or ''
    if CurrencyCode == '' :
      return
    self.ShowProgramData()

  def CurrencyAfterLookup(self,sender,linkUI):
    ProductId = self.uipProductAccount.GetFieldValue('LZakatProduct.ProductId') or ''
    if ProductId == '' :
      return
    self.ShowProgramData()

  # ----- SELF DEFINED METHOD
  def Show(self):
    return self.FormContainer.Show()

  def ShowProgramData(self):
    ProductId = self.uipProductAccount.GetFieldValue('LZakatProduct.ProductId')
    CurrencyCode = self.uipProductAccount.GetFieldValue('LCurrency.Currency_Code')

    ph = self.form.CallServerMethod(
        'GetProductData',
        self.app.CreateValues(
          ['ProductId',ProductId],
          ['CurrencyCode',CurrencyCode],
        )
    )

    rec = ph.FirstRecord

    if rec.Is_Err : raise 'PERINGATAN',rec.Err_Message

    uipProgram = self.uipProductAccount
    uipProgram.Edit()
    uipProgram.Balance = rec.Balance
    uipProgram.AccountNo = rec.AccountNo

    uipProgram.BranchName = rec.BranchName
    self.uipTransaction.ClearData()

    self.pFilterTransaction_BeginDate.SetFocus()

  def ViewHistTransaction(self,mode,filename=None):
    app = self.app
    
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['AccountNo', self.uipProductAccount.AccountNo],
        ['BeginDate', self.uipProductAccount.BeginDate],
        ['EndDate', self.uipProductAccount.EndDate]
      )
    )



    ds = ph.packet.histori
    if mode == 1 :
      uipData = self.uipProductAccount
      uipData.Edit()
      uipData.BeginningBalance = ph.FirstRecord.BeginningBalance
      uipData.TotalDebet = ph.FirstRecord.TotalDebet
      uipData.TotalCredit = ph.FirstRecord.TotalCredit
      
      uipTran = self.uipTransaction
      uipTran.ClearData()

      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        uipTran.Append()

        uipTran.TransactionItemId = rec.TransactionItemId
        uipTran.TransactionDate   = rec.TransactionDate
        uipTran.TransactionCode   = rec.TransactionCode
        uipTran.TransactionNo     = rec.TransactionNo
        uipTran.MutationType      = rec.MutationType
        uipTran.Amount            = rec.Amount
        uipTran.ReferenceNo       = rec.ReferenceNo
        uipTran.Description       = rec.Description
        uipTran.Inputer           = rec.Inputer

        i += 1
      # end of while

      uipTran.First()

    else:
      workbook = self.oPrint.OpenExcelTemplate(app,'tplHistTransZakat.xls')
      workbook.ActivateWorksheet('data')
      try:
        BeginingBalance = ph.FirstRecord.BeginningBalance
        PeriodStr = ph.FirstRecord.PeriodStr
        TotalDebet = ph.FirstRecord.TotalDebet
        TotalCredit = ph.FirstRecord.TotalCredit

        # SET HEADER
        uipData = self.uipProductAccount
        workbook.SetCellValue(2, 2, uipData.GetFieldValue('LZakatProduct.ProductName'))
        workbook.SetCellValue(3, 2, PeriodStr)
        workbook.SetCellValue(4, 2, BeginingBalance)
        workbook.SetCellValue(5, 2, TotalDebet)
        workbook.SetCellValue(6, 2, TotalCredit)
        workbook.SetCellValue(7, 2, BeginingBalance - TotalDebet + TotalCredit)

        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 10
          #workbook.SetCellValue(row, 1, rec.TransactionItemId)
          workbook.SetCellValue(row, 1, rec.TransactionDateStr)
          workbook.SetCellValue(row, 2, rec.TransactionNo)
          workbook.SetCellValue(row, 3, rec.MutationType)
          workbook.SetCellValue(row, 4, rec.Amount)
          workbook.SetCellValue(row, 5, rec.Description)
          workbook.SetCellValue(row, 6, rec.Inputer)
          workbook.SetCellValue(row, 7, rec.ReferenceNO)

          i += 1
        # end of while

        workbook.SaveAs(filename)
        app.ShellExecuteFile(filename)
        
      finally:
        # close
        workbook = None


