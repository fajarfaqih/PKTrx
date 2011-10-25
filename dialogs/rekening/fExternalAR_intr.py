class fExternalAR:
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
    if filename in [None,''] : return

    self.ViewHistTransaction(2,filename)

  def ViewHistTransaction(self,mode,filename=None):
    uipData = self.uipExternalAR

    if uipData.BeginDate > uipData.EndDate :
       raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'
       
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['AccountNo', uipData.GetFieldValue('LExternalAR.AccountNo')],
        ['BeginDate', uipData.BeginDate],
        ['EndDate', uipData.EndDate]
      )
    )

    ds = ph.packet.histori
    
    if ds.RecordCount <= 0 :
      self.app.ShowMessage('Tidak ada transaksi')

    if mode == 1 :
      self.uipExternalAR.BeginningBalance = ph.FirstRecord.BeginningBalance
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

      workbook = self.oPrint.OpenExcelTemplate(self.app,'tplHistTransExternalAR.xls')
      workbook.ActivateWorksheet('data')
      try:
        BeginingBalance = ph.FirstRecord.BeginningBalance
        PeriodStr = ph.FirstRecord.PeriodStr
        TotalDebet = ph.FirstRecord.TotalDebet
        TotalCredit = ph.FirstRecord.TotalCredit
        TotalBalance = ph.FirstRecord.TotalBalance
      
        workbook.SetCellValue(2, 2, uipData.GetFieldValue('LExternalAR.AccountName'))
        workbook.SetCellValue(3, 2, PeriodStr)
        workbook.SetCellValue(4, 2, BeginingBalance)
        workbook.SetCellValue(5, 2, TotalDebet)
        workbook.SetCellValue(6, 2, TotalCredit)
        workbook.SetCellValue(7, 2, TotalBalance)
        
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 10

          workbook.SetCellValue(row, 1, rec.TransactionDateStr)
          workbook.SetCellValue(row, 2, rec.TransactionNo)
          workbook.SetCellValue(row, 3, rec.Debet)
          workbook.SetCellValue(row, 4, rec.Kredit)
          workbook.SetCellValue(row, 5, rec.Description)
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

