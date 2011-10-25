class fDaftarProject:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.oPrint = None
    
  def Show(self):
    self.DisplayData()
    self.FormContainer.Show()

  def DisplayData(self):

    self.qProject.OQLText = "\
       select from ProjectAccount \
       [ \
         (  LProduct.Status = 'A' \
             or \
            LProduct.Status = 'N' ) \
            and BranchCode= '%s' \
        ] \
      ( \
        AccountNo as Kode_Proyek, \
        AccountName as Nama_Produk, \
        StartDate as Tgl_Mulai, \
        FinishDate as Tgl_Akhir, \
        BudgetAmount as Nilai_Budget, \
        Status $, \
        self \
      ) then order by Kode_Proyek; " % (self.uipFilter.BranchCode)
    self.qProject.DisplayData()

  def bExportExcelClick(self,sender):
    form = self.form
    app = self.app

    if self.oPrint == None :
      self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return

    resp = form.CallServerMethod(
         'GetDataProject',
         app.CreatePacket()
    )

    status = resp.FirstRecord

    if status.IsErr : raise 'PERINGATAN',status.ErrMessage


    workbook = self.oPrint.OpenExcelTemplate(app,'tplMasterProjectD.xls')
    workbook.ActivateWorksheet('data')

    try:
      ds = resp.packet.MasterData

      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        row = i + 4

        workbook.SetCellValue(row, 1, rec.ProductCode)
        workbook.SetCellValue(row, 2, rec.ProductName)
        workbook.SetCellValue(row, 3, rec.ProductNameParent)
        workbook.SetCellValue(row, 4, rec.Status)

        i += 1
      # end of while

      workbook.SaveAs(filename)
      app.ShellExecuteFile(filename)

    finally:
      # close
      workbook = None

