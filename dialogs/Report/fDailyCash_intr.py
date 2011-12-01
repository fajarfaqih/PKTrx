class fDailyCash:
  def __init__(self, formObj, parentForm):
    self.app=formObj.ClientApplication
    self.userapp = self.app.UserAppObject
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

  def Show(self):
    IsHeadOffice = self.uipData.BranchCode == '001'
    self.PData_LBranch.Enabled = IsHeadOffice
    return self.FormContainer.Show()

  def BranchAfterLookup(self,sender, linkui):
    self.uipData.Edit()
    self.uipData.BranchCode = self.uipData.GetFieldValue('LBranch.BranchCode') or ''
    
  def CheckInput(self):
    AccountNo = self.uipData.GetFieldValue('LCashAccount.AccountNo') or ''
    if AccountNo == '' : raise 'PERINGATAN','Silahkan pilih dahulu rekening kas'

  def PrintTextClick(self,sender) :
    self.FormObject.CommitBuffer()

    self.CheckInput()
    
    ph = self.FormObject.GetDataPacket()
    ph = self.app.ExecuteScript("Report/S_DailyCash.PrintText", ph)
    sw = ph.Packet.GetStreamWrapper(0)

    fileName = self.app.SaveFileDialog("Save to file..", "Format File(*.txt)|*.txt")

    if fileName.find(".txt") == -1 : fileName += ".txt"
    sw.SaveToFile(fileName)

    self.app.ShellExecuteFile(fileName)
    #sender.ExitAction = 1

    return 1

  def PrintExcelClick(self,sender):
    app = self.app
    self.FormObject.CommitBuffer()
    
    self.CheckInput()

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return

    ph = self.FormObject.GetDataPacket()
    ph = self.app.ExecuteScript("Report/S_DailyCash.PrintExcel", ph)

    status = ph.FirstRecord
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message
      
    workbook = self.oPrint.OpenExcelTemplate(app,'tplDailyCashReport.xls')
    workbook.ActivateWorksheet('data')
    
    try:

      workbook.SetCellValue(2, 2, status.StrDate)
      workbook.SetCellValue(3, 2, self.uipData.GetFieldValue('LCashAccount.AccountName'))
      workbook.SetCellValue(4, 2, status.Branch)
      workbook.SetCellValue(5, 2, status.Currency)
      workbook.SetCellValue(6, 2, status.BeginBalance)
      workbook.SetCellValue(7, 2, status.TotalDebet)
      workbook.SetCellValue(8, 2, status.TotalCredit)
      workbook.SetCellValue(9, 2, status.EndBalance)

      BBalance = status.BeginBalance
      ds = ph.packet.ReportData
      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        row = i + 12

        workbook.SetCellValue(row, 1, rec.BatchNo)
        workbook.SetCellValue(row, 2, rec.TransactionDateStr)
        workbook.SetCellValue(row, 3, rec.MutationType)
        workbook.SetCellValue(row, 4, rec.Amount)
        workbook.SetCellValue(row, 5, rec.Balance)
        workbook.SetCellValue(row, 6, rec.TransactionNo)
        workbook.SetCellValue(row, 7, rec.Description)
        workbook.SetCellValue(row, 8, rec.ReferenceNo)
        workbook.SetCellValue(row, 9, rec.Inputer)
        workbook.SetCellValue(row, 10, rec.AuthStatus)

        i += 1
      # end while

      workbook.SaveAs(filename)

    finally:
      workbook = None

    app.ShellExecuteFile(filename)
