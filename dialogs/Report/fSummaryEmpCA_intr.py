class fSummaryCashAdvance:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.userapp = self.app.UserAppObject
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

  def Show(self):
    #-- Set Branch Filter
    uipData = self.uipData
    uipData.Edit()
    IsHeadOffice = (uipData.UserBranchCode == uipData.HeadOfficeCode)
    self.MasterBranchCode = ''

    if not IsHeadOffice :
      uipData.MasterBranchCode = uipData.UserBranchCode

    uipData.SetFieldValue('LBranch.BranchCode',uipData.UserBranchCode)
    uipData.SetFieldValue('LBranch.BranchName',uipData.UserBranchName)

    #-- Set Default Value
    uipData.IsAllBranch = 'F'
    
    return self.FormContainer.Show()

  def IsAllBranchClick(self, sender):
    uipData = self.uipData
    if sender.Checked:
      uipData.SetFieldValue('LBranch.BranchCode','')
      uipData.SetFieldValue('LBranch.BranchName','')
    # end if
    self.pData_LBranch.enabled = not sender.Checked
    
  def CheckRequired(self):
    uipData = self.uipData

    BranchCode = uipData.GetFieldValue('LBranch.BranchCode')

    if uipData.IsAllBranch == 'F' and BranchCode in [None,''] :
      raise 'PERINGATAN','Anda belum memilih cabang.'

    if uipData.BeginDate > uipData.EndDate :
      raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'

  def PrintExcelClick(self,sender) :
    uipData = self.uipData
    app = self.FormObject.ClientApplication

    filename = self.oPrint.ConfirmDestinationPath(self.app,'xls')
    if filename in ['',None] : return

    self.FormObject.CommitBuffer()
    self.CheckRequired()

    # -- Generate Param
    param = self.FormObject.GetDataPacket()
    ph = self.FormObject.CallServerMethod("SummaryEmpCA", param)

    status = ph.FirstRecord
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message
    
    ds = ph.packet.summary
    if ds.RecordCount <= 0 :
      self.app.ShowMessage('Tidak ada data untuk dicetak')
      return
      
    workbook = self.oPrint.OpenExcelTemplate(self.app,'tplSumEmployeeCA.xls')
    try:
      workbook.ActivateWorksheet('DataRekap')
      BranchCode = uipData.GetFieldValue('LBranch.BranchCode')
      BranchName = status.BranchName
      PeriodStr = status.PeriodStr

      #--- Set Branch Header Info
      if uipData.IsAllBranch == 'F' :
        workbook.SetCellValue(2, 2, '%s - %s' % (BranchCode,BranchName))
        workbook.SetCellValue(9, 1, '') # Kosongkan keterangan Total
      else:
        IsHeadOffice = (uipData.UserBranchCode == uipData.HeadOfficeCode)
        if not IsHeadOffice :
          workbook.SetCellValue(2, 2, '%s (Konsolidasi KCP)' % (BranchName))
        else:
          workbook.SetCellValue(2, 2, 'Seluruh Cabang')
      # end if
      
      workbook.SetCellValue(3, 2, PeriodStr) # Nomor Karyawan
      workbook.SetCellValue(4, 2, status.BeginBalanceEkuiv) # Nomor Karyawan
      workbook.SetCellValue(5, 2, status.TotalDebetEkuiv)
      workbook.SetCellValue(6, 2, status.TotalCreditEkuiv)
      workbook.SetCellValue(7, 2, status.EndBalanceEkuiv)
      
      workbook.SetCellValue(11, 4, 'Saldo Awal \n' + status.BeginDateStr)
      workbook.SetCellValue(11, 8, 'Saldo Akhir \n' + status.EndDateStr)

      i = 0
      oldIdNumber = 0
      row = 12
      rowTotalGroup = 2
      PrevBranchCode = ''
      PrevBranchName = ''
      TotalSaldoAwalGroup = 0.0
      TotalDebetGroup = 0.0
      TotalCreditGroup = 0.0
      TotalMutasiGroup = 0.0
      TotalSaldoAkhirGroup = 0.0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)

        if oldIdNumber != rec.NomorKaryawan :
          workbook.SetCellValue(row, 1, rec.NomorKaryawan)
          workbook.SetCellValue(row, 2, rec.NamaKaryawan)
          oldIdNumber = rec.NomorKaryawan

        if PrevBranchCode != rec.BranchCode :
          if PrevBranchCode != '' :
            workbook.ActivateWorksheet('TotalPerCabang')
            workbook.SetCellValue(rowTotalGroup, 1, PrevBranchCode)
            workbook.SetCellValue(rowTotalGroup, 2, PrevBranchName)
            workbook.SetCellValue(rowTotalGroup, 3, TotalSaldoAwalGroup)
            workbook.SetCellValue(rowTotalGroup, 4, TotalDebetGroup)
            workbook.SetCellValue(rowTotalGroup, 5, TotalCreditGroup)
            workbook.SetCellValue(rowTotalGroup, 6, TotalMutasiGroup)
            workbook.SetCellValue(rowTotalGroup, 7, TotalSaldoAkhirGroup)
            workbook.ActivateWorksheet('DataRekap')
            
            TotalSaldoAwalGroup = 0.0
            TotalDebetGroup = 0.0
            TotalCreditGroup = 0.0
            TotalMutasiGroup = 0.0
            TotalSaldoAkhirGroup = 0.0

            rowTotalGroup += 1
          # end if
          PrevBranchCode = rec.BranchCode
          PrevBranchName = rec.BranchName
        # end if

        workbook.SetCellValue(row, 3, rec.CurrencyName)
        workbook.SetCellValue(row, 4, rec.SaldoAwal)
        workbook.SetCellValue(row, 5, rec.Debet)
        workbook.SetCellValue(row, 6, rec.Kredit)
        workbook.SetCellValue(row, 7, rec.TotalMutasi)
        workbook.SetCellValue(row, 8, rec.SaldoAkhir)
        workbook.SetCellValue(row, 9, rec.BranchName)
        
        TotalSaldoAwalGroup += rec.SaldoAwal
        TotalDebetGroup += rec.Debet
        TotalCreditGroup += rec.Kredit
        TotalMutasiGroup += rec.TotalMutasi
        TotalSaldoAkhirGroup += rec.SaldoAkhir
        
        i += 1
        row += 1
      # end of while
      workbook.ActivateWorksheet('TotalPerCabang')
      workbook.SetCellValue(rowTotalGroup, 1, PrevBranchCode)
      workbook.SetCellValue(rowTotalGroup, 2, PrevBranchName)
      workbook.SetCellValue(rowTotalGroup, 3, TotalSaldoAwalGroup)
      workbook.SetCellValue(rowTotalGroup, 4, TotalDebetGroup)
      workbook.SetCellValue(rowTotalGroup, 5, TotalCreditGroup)
      workbook.SetCellValue(rowTotalGroup, 6, TotalMutasiGroup)
      workbook.SetCellValue(rowTotalGroup, 7, TotalSaldoAkhirGroup)
      workbook.ActivateWorksheet('DataRekap')


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
        workbook.SetCellValue(row, 13, rec.BranchName)

        i += 1
      # end while

      # set sheet aktif
      workbook.ActivateWorksheet('DataRekap')
      
      workbook.SaveAs(filename)
      self.app.ShellExecuteFile(filename)

    finally:
      workbook = None

    return 1

