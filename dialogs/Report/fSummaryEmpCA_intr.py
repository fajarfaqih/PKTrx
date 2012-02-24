class fSummaryCashAdvance:
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
    if filename in ['',None] : return

    self.FormObject.CommitBuffer()
    ph = self.FormObject.GetDataPacket()
    ph = self.FormObject.CallServerMethod("SummaryEmpCA", ph)

    status = ph.FirstRecord
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message
    
    ds = ph.packet.summary
    if ds.RecordCount <= 0 :
      self.app.ShowMessage('Tidak ada data untuk dicetak')
      return
      
    workbook = self.oPrint.OpenExcelTemplate(self.app,'tplSumEmployeeCA.xls')
    try:
      workbook.ActivateWorksheet('DataRekap')
      BranchCode = self.uipData.BranchCode
      BranchName = status.BranchName
      PeriodStr = status.PeriodStr

      workbook.SetCellValue(2, 2, '%s - %s' % (BranchCode,BranchName))
      workbook.SetCellValue(3, 2, PeriodStr) # Nomor Karyawan
      workbook.SetCellValue(4, 2, status.BeginBalance) # Nomor Karyawan
      workbook.SetCellValue(5, 2, status.TotalDebet)
      workbook.SetCellValue(6, 2, status.TotalCredit)
      workbook.SetCellValue(7, 2, status.EndBalance)
      
      workbook.SetCellValue(9, 4, 'Saldo Awal \n' + status.BeginDateStr)
      workbook.SetCellValue(9, 8, 'Saldo Akhir \n' + status.EndDateStr)
      i = 0
      oldIdNumber = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        row = i + 11

        if oldIdNumber != rec.NomorKaryawan :
          workbook.SetCellValue(row, 1, rec.NomorKaryawan)
          workbook.SetCellValue(row, 2, rec.NamaKaryawan)
          oldIdNumber = rec.NomorKaryawan

        workbook.SetCellValue(row, 3, rec.CurrencyName)
        workbook.SetCellValue(row, 4, rec.SaldoAwal)
        workbook.SetCellValue(row, 5, rec.Debet)
        workbook.SetCellValue(row, 6, rec.Kredit)
        workbook.SetCellValue(row, 7, rec.TotalMutasi)
        workbook.SetCellValue(row, 8, rec.SaldoAkhir)
        i += 1
      # end of while


      # ---- Data Histori
      dsHistTrans = ph.packet.historitransaksi
      workbook.ActivateWorksheet('DetilTransaksi')

      workbook.SetCellValue(1, 2, status.TotalDebetHist)
      workbook.SetCellValue(2, 2, status.TotalCreditHist)

      i = 0
      TotalTransaksi = dsHistTrans.RecordCount
      while i < TotalTransaksi:
        rec = dsHistTrans.GetRecord(i)
        row = i + 5

        workbook.SetCellValue(row, 1, rec.TransactionDateStr)
        workbook.SetCellValue(row, 2, rec.TransactionNo)
        workbook.SetCellValue(row, 3, rec.AccountName)
        workbook.SetCellValue(row, 4, rec.MutationType)
        workbook.SetCellValue(row, 5, rec.Amount)
        workbook.SetCellValue(row, 6, rec.CurrencyName)
        workbook.SetCellValue(row, 7, rec.AmountEkuivalen)
        workbook.SetCellValue(row, 8, rec.ReferenceNo)
        workbook.SetCellValue(row, 9, rec.Description)
        workbook.SetCellValue(row, 10, rec.ReturnStatus)
        workbook.SetCellValue(row, 11, rec.ReturnTransactionNo)
        workbook.SetCellValue(row, 12, rec.Inputer)

        i += 1
      # end while

      # set sheet aktif
      workbook.ActivateWorksheet('DataRekap')
      
      workbook.SaveAs(filename)
      self.app.ShellExecuteFile(filename)

    finally:
      workbook = None

    return 1

