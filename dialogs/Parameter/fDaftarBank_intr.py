class fDaftarBank:
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


    workbook = self.oPrint.OpenExcelTemplate(app,'tplMasterBank.xls')
    workbook.ActivateWorksheet('data')

    try:
      ds = resp.packet.MasterData

      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        row = i + 4

        workbook.SetCellValue(row, 1, rec.BankCode)
        workbook.SetCellValue(row, 2, rec.BankName)
        workbook.SetCellValue(row, 3, rec.BankShortName)
        
        i += 1
      # end of while

      workbook.SaveAs(filename)
      app.ShellExecuteFile(filename)

    finally:
      # close
      workbook = None


    
