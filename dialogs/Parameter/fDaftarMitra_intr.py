class fDaftarMitra:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.oPrint = None

  def FormOnShow(self,sender):
    self.DisplayQuery()

  def bExportExcelClick(self,sender):
    form = self.form
    app = self.app

    if self.oPrint == None :
      self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename == '' : return

    resp = form.CallServerMethod(
         'GetDataMitra',
         app.CreatePacket()
    )

    status = resp.FirstRecord

    if status.IsErr : raise 'PERINGATAN',status.ErrMessage


    workbook = self.oPrint.OpenExcelTemplate(app,'tplMasterMitra.xls')
    workbook.ActivateWorksheet('data')

    try:
      ds = resp.packet.MasterData

      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        row = i + 4

        workbook.SetCellValue(row, 1, rec.VolunteerId)
        workbook.SetCellValue(row, 2, rec.VolunteerName)
        workbook.SetCellValue(row, 3, rec.Email)
        workbook.SetCellValue(row, 4, rec.BranchCode)
        workbook.SetCellValue(row, 5, rec.BranchName)
        i += 1
      # end of while

      workbook.SaveAs(filename)
      app.ShellExecuteFile(filename)

    finally:
      # close
      workbook = None


  def DisplayQuery(self):
    BranchCode = self.uipParam.BranchCode
    qVolunteer = self.fVolunteer
    qVolunteer.OQLText = " select from Volunteer \
        [BranchCode = '%s'] \
        ( \
          VolunteerId, \
          VolunteerName as Nama_Mitra, \
          Email, \
          BranchCode, \
          self \
        ) then order by VolunteerId; \
    " % (BranchCode)

    qVolunteer.DisplayData()


