class fDaftarRekeningKasCabang:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.oPrint = None

  def bExportExcelClick(self,sender):
    form = self.form
    app = self.app

    if self.oPrint == None :
      self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return

    resp = form.CallServerMethod(
         'GetDataBank',
         app.CreatePacket()
    )

    status = resp.FirstRecord

    if status.IsErr : raise 'PERINGATAN',status.ErrMessage


    workbook = self.oPrint.OpenExcelTemplate(app,'tplMasterRekeningKasCabang.xls')
    workbook.ActivateWorksheet('data')

    try:
      ds = resp.packet.MasterData

      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        row = i + 4

        workbook.SetCellValue(row, 1, rec.AccountNo)
        workbook.SetCellValue(row, 2, rec.CashCode)
        workbook.SetCellValue(row, 3, rec.AccountName)
        workbook.SetCellValue(row, 4, rec.BranchCode)
        workbook.SetCellValue(row, 5, rec.BranchName)
        workbook.SetCellValue(row, 6, rec.CurrencyCode)
        workbook.SetCellValue(row, 7, rec.CurrencyName)
        workbook.SetCellValue(row, 8, rec.Balance)
        workbook.SetCellValue(row, 9, rec.Status)


        i += 1
      # end of while

      workbook.SaveAs(filename)
      app.ShellExecuteFile(filename)

    finally:
      # close
      workbook = None

