class fSummaryEmpAR:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.userapp = self.app.UserAppObject
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

  def Show(self):
    return self.FormContainer.Show()


  def PrintExcelClick(self,sender) :
    if self.uipData.BeginDate > self.uipData.EndDate :
       raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'

    filename = self.oPrint.ConfirmDestinationPath(self.app,'xls')
    if filename == '' : return

    self.FormObject.CommitBuffer()
    ph = self.FormObject.GetDataPacket()
    ph = self.FormObject.CallServerMethod("SummaryEmpAr", ph)

    status = ph.FirstRecord
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message
    
    ds = ph.packet.summary
    if ds.RecordCount <= 0 :
      self.app.ShowMessage('Tidak ada data untuk dicetak')
      return
      
    workbook = self.oPrint.OpenExcelTemplate(self.app,'tplSumEmployeeAR.xls')
    workbook.ActivateWorksheet('data')
    try:
      BranchCode = self.uipData.BranchCode
      BranchName = status.BranchName
      PeriodStr = status.PeriodStr

      workbook.SetCellValue(2, 2, '%s - %s' % (BranchCode,BranchName))
      workbook.SetCellValue(3, 2, PeriodStr) # Nomor Karyawan
      workbook.SetCellValue(4, 2, status.BeginBalance) # Nomor Karyawan
      workbook.SetCellValue(5, 2, status.TotalDebet)
      workbook.SetCellValue(6, 2, status.TotalCredit)
      workbook.SetCellValue(7, 2, status.EndBalance)
      
      workbook.SetCellValue(9, 3, 'Saldo Awal \n' + status.BeginDateStr)
      workbook.SetCellValue(9, 7, 'Saldo Akhir \n' + status.EndDateStr)
      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        row = i + 10

        workbook.SetCellValue(row, 1, rec.NomorKaryawan)
        workbook.SetCellValue(row, 2, rec.NamaKaryawan)
        workbook.SetCellValue(row, 3, rec.SaldoAwal)
        workbook.SetCellValue(row, 4, rec.Debet)
        workbook.SetCellValue(row, 5, rec.Kredit)
        workbook.SetCellValue(row, 6, rec.TotalMutasi)
        workbook.SetCellValue(row, 7, rec.SaldoAkhir)
        i += 1
      # end of while


      workbook.SaveAs(filename)
      self.app.ShellExecuteFile(filename)

    finally:
      workbook = None

    return 1

