class fGLAccount:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  def Show(self):
    return self.FormContainer.Show()

  def bViewHistClick (self, sender):
    self.ViewHistTransaction(1)

  def bExportClick(self,sender):
    app = self.app

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename == '' : return

    self.ViewHistTransaction(2,filename)

  def ViewHistTransaction(self,mode,filename=None):
    uipData = self.uipGLAccount

    if uipData.BeginDate > uipData.EndDate :
       raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'
       
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['AccountNo', uipData.GetFieldValue('LGLAccount.Account_Code')],
        ['BeginDate', uipData.BeginDate],
        ['EndDate', uipData.EndDate]
      )
    )

    ds = ph.packet.histori
    
    if ds.RecordCount <= 0 :
      self.app.ShowMessage('Tidak ada transaksi')

    if mode == 1 :
      self.uipGLAccount.BeginningBalance = ph.FirstRecord.BeginningBalance
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
        uipTran.AuthStatus        = rec.AuthStatus

        i += 1
      # end of while

      uipTran.First()

    else:

      workbook = self.oPrint.OpenExcelTemplate(self.app,'tplHistTransGLAccount.xls')
      workbook.ActivateWorksheet('data')
      try:
        BeginingBalance = ph.FirstRecord.BeginningBalance
        PeriodStr = ph.FirstRecord.PeriodStr
        TotalBalance = ph.FirstRecord.TotalBalance
        TotalDebet = ph.FirstRecord.TotalDebet
        TotalCredit = ph.FirstRecord.TotalCredit
      
        workbook.SetCellValue(2, 2, uipData.GetFieldValue('LGLAccount.Account_Code'))
        workbook.SetCellValue(3, 2, uipData.GetFieldValue('LGLAccount.Account_Name'))
        workbook.SetCellValue(4, 2, PeriodStr)
        workbook.SetCellValue(5, 2, BeginingBalance)
        workbook.SetCellValue(6, 2, TotalDebet)
        workbook.SetCellValue(7, 2, TotalCredit)
        #workbook.SetCellValue(8, 2, TotalBalance)
        
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 11

          workbook.SetCellValue(row, 1, rec.TransactionDateStr)
          workbook.SetCellValue(row, 2, rec.Debet)
          workbook.SetCellValue(row, 3, rec.Kredit)
          workbook.SetCellValue(row, 4, rec.Description)
          workbook.SetCellValue(row, 5, rec.TransactionNo)
          workbook.SetCellValue(row, 6, rec.Inputer)
          workbook.SetCellValue(row, 7, rec.ReferenceNo)
          workbook.SetCellValue(row, 8, rec.AuthStatus)
          i += 1
        # end of while

        
        workbook.SaveAs(filename)
        self.app.ShellExecuteFile(filename)
      finally:
        # close
        workbook = None

