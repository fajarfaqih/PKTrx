class fDaftarProdukZakat:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.oPrint = None

  def bCloseClick(self,sender):
    self.FormObject.Close(2)
    
  def bExportExcelClick(self,sender):
    form = self.form
    app = self.app

    if self.oPrint == None :
      self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return
    
    resp = form.CallServerMethod(
         'GetDataProdukZakat',
         app.CreatePacket()
    )

    status = resp.FirstRecord
    
    if status.IsErr : raise 'PERINGATAN',status.ErrMessage
    

    workbook = self.oPrint.OpenExcelTemplate(app,'tplMasterZakat.xls')
    workbook.ActivateWorksheet('data')

    try:
      ds = resp.packet.MasterData

      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        row = i + 4

        workbook.SetCellValue(row, 1, rec.ProductCode)
        workbook.SetCellValue(row, 2, rec.Description)
        workbook.SetCellValue(row, 3, rec.Rate)
        workbook.SetCellValue(row, 4, rec.PercentageOfAmilFunds)
        workbook.SetCellValue(row, 5, rec.Status)
        workbook.SetCellValue(row, 6, rec.Level)
        workbook.SetCellValue(row, 7, rec.IsDetail)

        i += 1
      # end of while

      workbook.SaveAs(filename)
      app.ShellExecuteFile(filename)

    finally:
      # close
      workbook = None


