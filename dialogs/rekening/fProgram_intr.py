Entities = ['Seluruhnya','Zakat','Infaq','Wakaf']

class fProgram:
  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  def Show(self):
    self.uipProductAccount.Edit()
    self.uipProductAccount.FundEntity = 0
    return self.FormContainer.Show()

  def ProgramAfterLookup(self,sender,linkUI):
    CurrencyCode = self.uipProductAccount.GetFieldValue('LCurrency.Currency_Code') or ''
    if CurrencyCode == '' :
      return
    self.ShowProgramData()
    
  def CurrencyAfterLookup(self,sender,linkUI):
    ProductId = self.uipProductAccount.GetFieldValue('LProductAccount.ProductId') or ''
    if ProductId == '' :
      return
    self.ShowProgramData()

  def ShowProgramData(self):
    ProductId = self.uipProductAccount.GetFieldValue('LProductAccount.ProductId')
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
    uipProgram.ZakatBalance = rec.ZakatBalance
    uipProgram.InfaqBalance = rec.InfaqBalance
    uipProgram.WakafBalance = rec.WakafBalance
    uipProgram.AmilBalance = rec.AmilBalance
    uipProgram.NonHalalBalance = rec.NonHalalBalance
    uipProgram.TotalBalance = rec.TotalBalance
    uipProgram.AccountNo = rec.AccountNo
    
    uipProgram.BranchName = rec.BranchName
    
    self.pSelectTransaction_BeginDate.SetFocus()

  def bViewHistClick (self, sender):
    self.ViewHistTransaction(1)

  def bExportClick(self,sender):
    app = self.app

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename == '' : return
    
    self.ViewHistTransaction(2,filename)

  def ViewHistTransaction(self,mode,filename=None):
    app = self.app
    uipData = self.uipProductAccount
    
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['AccountNo', uipData.AccountNo],
        ['FundEntity', uipData.FundEntity],
        ['BeginDate', uipData.BeginDate],
        ['EndDate', uipData.EndDate]
      )
    )

    ds = ph.packet.histori

    if ds.RecordCount <= 0 :
      app.ShowMessage('Tidak ada transaksi')
      return
    
    if mode == 1 : # MODE GRID -- SET LIST TRANSACTION TO GRID
      recStatus = ph.FirstRecord
      uipData.BeginningBalance = recStatus.BeginningBalance
      
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
      

      uipData.TotalDebet =  recStatus.TotalDebet
      uipData.TotalCredit =  recStatus.TotalCredit
      uipData.EndBalance =  recStatus.BeginningBalance - recStatus.TotalDebet + recStatus.TotalCredit

    else: # MODE EXPORT EXCEL -- SET LIST TRANSACTION TO EXCEL
      workbook = self.oPrint.OpenExcelTemplate(app,'tplHistTransProgram.xls')
      workbook.ActivateWorksheet('data')
      try:
        BeginingBalance = ph.FirstRecord.BeginningBalance
        PeriodStr = ph.FirstRecord.PeriodStr
        TotalDebet = ph.FirstRecord.TotalDebet
        TotalCredit = ph.FirstRecord.TotalCredit
        
        # SET HEADER
        workbook.SetCellValue(2, 2, uipData.GetFieldValue('LProductAccount.LProduct.ProductName'))
        workbook.SetCellValue(3, 2, Entities[uipData.FundEntity])
        workbook.SetCellValue(4, 2, PeriodStr)
        workbook.SetCellValue(5, 2, BeginingBalance)
        workbook.SetCellValue(6, 2, TotalDebet)
        workbook.SetCellValue(7, 2, TotalCredit)
        workbook.SetCellValue(8, 2, BeginingBalance - TotalDebet + TotalCredit)
        
        # SET DETAIL
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 11
          
          workbook.SetCellValue(row, 1, rec.TransactionDateStr)
          workbook.SetCellValue(row, 2, rec.Debet)
          workbook.SetCellValue(row, 3, rec.Kredit)
          workbook.SetCellValue(row, 4, rec.Description)
          workbook.SetCellValue(row, 5, rec.TransactionNo)
          workbook.SetCellValue(row, 6, rec.JenisTransaksi)
          workbook.SetCellValue(row, 7, rec.Inputer)
          workbook.SetCellValue(row, 8, rec.ReferenceNo)


          i += 1
        # end of while

        workbook.SaveAs(filename)
        app.ShellExecuteFile(filename)
        
      finally:
        # close
        workbook = None
