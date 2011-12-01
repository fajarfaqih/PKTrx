class fEmployeeCashAdvance:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  def Show(self):
    return self.FormContainer.Show()

  def EmployeeAfterLookup(self, sender, linkui):
    form = self.form
    app = self.app
    uipEmployeeAR = self.uipEmployeeAR
        
    params = app.CreateValues(['EmployeeId',uipEmployeeAR.GetFieldValue('LEmployeeAR.EmployeeId')])
    
    rph = form.CallServerMethod('GetCashAdvanceBalance',params)
    
    status = rph.FirstRecord
    
    if status.IsErr : raise 'PERINGATAN',status.ErrMessage
    
    uipEmployeeAR.Edit()
    uipEmployeeAR.Balance = status.Balance
    
  
  def bViewHistClick (self, sender):
    self.ViewHistTransaction(1)

  def bExportClick(self,sender):
    app = self.app

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename == '' : return

    self.ViewHistTransaction(2,filename)

  def ViewHistTransaction(self,mode,filename=None):
    uipData = self.uipEmployeeAR

    if uipData.BeginDate > uipData.EndDate :
       raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'
       
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['EmployeeId',uipData.GetFieldValue('LEmployeeAR.EmployeeId')],
        ['BeginDate', uipData.BeginDate],
        ['EndDate', uipData.EndDate]
      )
    )

    ds = ph.packet.histori
    
    if ds.RecordCount <= 0 :
      app.ShowMessage('Tidak ada transaksi')

    if mode == 1 :
      self.uipEmployeeAR.BeginningBalance = ph.FirstRecord.BeginningBalance
      uipTran = self.uipTransaction
      uipTran.ClearData()
      
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
        uipTran.TransactionNo     = rec.TransactionNo
        uipTran.CurrencyName      = rec.CurrencyName
        uipTran.Rate              = rec.Rate
        uipTran.AmountEkuivalen   = rec.AmountEkuivalen

        i += 1
      # end of while

      uipTran.First()

    else:

      workbook = self.oPrint.OpenExcelTemplate(self.app,'tplHistTransEmployeeCA.xls')
      workbook.ActivateWorksheet('data')
      try:
        BeginingBalance = ph.FirstRecord.BeginningBalance
        PeriodStr = ph.FirstRecord.PeriodStr
        TotalBalance = ph.FirstRecord.TotalBalance
        TotalDebet = ph.FirstRecord.TotalDebet
        TotalCredit = ph.FirstRecord.TotalCredit
      
        workbook.SetCellValue(2, 2, uipData.GetFieldValue('LEmployeeAR.EmployeeName'))
        workbook.SetCellValue(3, 2, '') # Nomor Karyawan
        workbook.SetCellValue(4, 2, PeriodStr)
        workbook.SetCellValue(5, 2, BeginingBalance)
        workbook.SetCellValue(6, 2, TotalDebet)
        workbook.SetCellValue(7, 2, TotalCredit)
        workbook.SetCellValue(8, 2, TotalBalance)
        
        
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 11

          workbook.SetCellValue(row, 1, rec.TransactionDateStr)
          workbook.SetCellValue(row, 2, rec.TransactionNo)
          workbook.SetCellValue(row, 3, rec.MutationType)
          workbook.SetCellValue(row, 4, rec.Amount)
          workbook.SetCellValue(row, 5, rec.CurrencyName)
          workbook.SetCellValue(row, 6, rec.AmountEkuivalen)
          workbook.SetCellValue(row, 7, rec.Description)
          workbook.SetCellValue(row, 8, rec.Inputer)
          workbook.SetCellValue(row, 9, rec.ReferenceNo)
          workbook.SetCellValue(row, 10, rec.AuthStatus)
          
          i += 1
        # end of while

        
        workbook.SaveAs(filename)
        self.app.ShellExecuteFile(filename)
      finally:
        # close
        workbook = None


