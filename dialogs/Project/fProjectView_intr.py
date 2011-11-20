class fProjectView:

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

  # ----- SELF DEFINED METHOD
  def Show(self):
    return self.FormContainer.Show()

  def ViewHistTransaction(self,mode,filename=None):
    app = self.app
    
    uipProject = self.uipProject
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['AccountNo', uipProject.AccountNo],
        ['BeginDate', uipProject.BeginDate],
        ['EndDate', uipProject.EndDate]
      )
    )

    ds = ph.packet.histori
    recStatus = ph.FirstRecord
    
    if mode == 1 :
      uipProject.Edit()
      uipProject.BeginningBalance = recStatus.BeginningBalance
      uipProject.TotalDebet = recStatus.TotalDebet
      uipProject.TotalCredit = recStatus.TotalCredit
      uipProject.EndBalance = recStatus.BeginningBalance - recStatus.TotalDebet + recStatus.TotalCredit
      
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
      workbook = self.oPrint.OpenExcelTemplate(app,'tplHistTransProject.xls')
      workbook.ActivateWorksheet('data')
      try:
      
        # SET HEADER
        workbook.SetCellValue(2, 2, "%s - %s" % (uipProject.AccountNo,uipProject.AccountName))
        workbook.SetCellValue(3, 2, recStatus.PeriodStr)
        workbook.SetCellValue(4, 2, recStatus.BeginningBalance)
        workbook.SetCellValue(5, 2, recStatus.TotalDebet)
        workbook.SetCellValue(5, 2, recStatus.TotalCredit)
        workbook.SetCellValue(7, 2, recStatus.BeginningBalance - recStatus.TotalDebet + recStatus.TotalCredit)
        
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
          workbook.SetCellValue(row, 7, rec.ReferenceNo)

          i += 1
        # end of while

        workbook.SaveAs(filename)
        app.ShellExecuteFile(filename)
        
      finally:
        # close
        workbook = None



