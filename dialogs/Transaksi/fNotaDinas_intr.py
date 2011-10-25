class fNotaDinas:
  def __init__(self,formObj,parentObj):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  #-- FORM OBJECT EVENT
  def bPrintClick(self,sender):
    app = self.app
    uipData = self.uipData
    
    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return
    
    self.FormObject.CommitBuffer()
    param = self.FormObject.GetDataPacket()
    
    resp = self.form.CallServerMethod('PrintNotaDinas',param)
    
    status = resp.FirstRecord
    if status.IsErr : raise 'PERINGATAN',status.ErrMessage
    
    workbook = self.oPrint.OpenExcelTemplate(app,'tplNotaDinas.xls')
    workbook.ActivateWorksheet('data')
    try:
      workbook.SetCellValue(7, 3, ': %s' % status.Nomor)
      workbook.SetCellValue(8, 3, ': %s' % status.Tanggal)
      workbook.SetCellValue(13, 6, status.BranchCashBalance)
      workbook.SetCellValue(13, 7, status.Tanggal)
      workbook.SetCellValue(14, 6, status.BankCashBalance)
      workbook.SetCellValue(14, 7, status.Tanggal)
      workbook.SetCellValue(15, 6, status.OtherBankBalance)
      workbook.SetCellValue(15, 7, status.Tanggal)
      workbook.SetCellValue(18, 6, status.TotalAmount)
      
      ds = resp.packet.NotaDinas
      TotalData = ds.RecordCount
      i = 0
      row = 0
      while i < TotalData :
        rec = ds.GetRecord(i)
        row = i + 22

        workbook.SetCellValue(row, 2, str(i+1))
        workbook.SetCellValue(row, 3, rec.COA)
        #workbook.SetCellValue(row, 3, rec.BudgetOwner)
        workbook.SetCellValue(row, 4, rec.BudgetCode)
        workbook.SetCellValue(row, 5, rec.FundEntity)
        workbook.SetCellValue(row, 6, rec.Description)
        workbook.SetCellValue(row, 7, rec.Nominal)
        workbook.SetCellValue(row, 8, rec.TransactionNo)

        i += 1
      # end while
      
      row += 1
      workbook.SetCellValue(row, 2, 'Total')
      workbook.SetCellValue(row, 7, status.TotalAmount)

      row += 2
      workbook.SetCellValue(row, 2, 'Dibayar Oleh')
      workbook.SetCellValue(row, 4, 'Diinput Oleh')
      workbook.SetCellValue(row, 6, 'Mengetahui')
      workbook.SetCellValue(row, 7, 'Disetujui')

      row += 5
      workbook.SetCellValue(row, 2, '(%s)' % uipData.PaidFrom)
      workbook.SetCellValue(row, 4, '(%s)' % uipData.Inputer)
      workbook.SetCellValue(row, 6, '(%s)' % uipData.Manajer)
      workbook.SetCellValue(row, 7, '(%s)' % uipData.Direktur)
      
      workbook.SaveAs(filename)

    finally:
      workbook = None

    app.ShellExecuteFile(filename)
  
  #-- USER DEFINED METHOD
  def Show(self):
    self.FormContainer.Show()
