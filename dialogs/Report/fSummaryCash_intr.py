class fSummaryCash:
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
    if self.uipData.BeginDate > self.uipData.EndDate :
       raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'

  def PrintClick(self,sender) :
    self.FormObject.CommitBuffer()
    self.CheckInput()
    ph = self.FormObject.GetDataPacket()
    ph = self.app.ExecuteScript("Report/S_SummaryCash.PrintText", ph)
    sw = ph.Packet.GetStreamWrapper(0)

    fileName = self.app.SaveFileDialog("Save to file..", "Format File(*.txt)|*.txt")
    if fileName.find(".txt") == -1 : fileName += ".txt"
    sw.SaveToFile(fileName)

    self.app.ShellExecuteFile(fileName)
    #sender.ExitAction = 1

    return 1
    
  def ExcelClick(self,sender):
    app = self.app
    self.FormObject.CommitBuffer()
    self.CheckInput()

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return



    ph = self.FormObject.GetDataPacket()
    ph = self.app.ExecuteScript("Report/S_SummaryCash.PrintExcel", ph)

    status = ph.FirstRecord
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message

    workbook = self.oPrint.OpenExcelTemplate(app,'tplSummaryCashReport.xls')
    workbook.ActivateWorksheet('data')

    try:

      workbook.SetCellValue(2, 2, status.Branch)
      workbook.SetCellValue(3, 2, status.PeriodDate)
      workbook.SetCellValue(4, 2, status.TotalBeginBalance)
      workbook.SetCellValue(5, 2, status.TotalDebet)
      workbook.SetCellValue(6, 2, status.TotalCredit)
      workbook.SetCellValue(7, 2, status.TotalEndBalance)

      Currencies = {}
      LastCurrency = ''
      ds = ph.packet.ReportData
      row = 10
      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)

        if not Currencies.has_key(rec.CurrencyName):
          Currencies[rec.CurrencyName] = {}
          Currencies[rec.CurrencyName]['TotalBegin'] = 0.0
          Currencies[rec.CurrencyName]['TotalCredit'] = 0.0
          Currencies[rec.CurrencyName]['TotalDebet'] = 0.0
          Currencies[rec.CurrencyName]['TotalEnd'] = 0.0
          
          if LastCurrency != '' :
            workbook.SetCellValue(row, 1, 'TOTAL VALUTA KAS/BANK ' + LastCurrency )
            workbook.SetCellValue(row, 2, '')
            #workbook.SetCellValue(row, 3, '')
            workbook.SetCellValue(row, 3, Currencies[LastCurrency]['TotalBegin'])
            workbook.SetCellValue(row, 4, Currencies[LastCurrency]['TotalDebet'])
            workbook.SetCellValue(row, 5, Currencies[LastCurrency]['TotalCredit'])
            workbook.SetCellValue(row, 6, Currencies[LastCurrency]['TotalDebet'] - Currencies[LastCurrency]['TotalCredit'])
            workbook.SetCellValue(row, 7, Currencies[LastCurrency]['TotalEnd'])

            row += 2
          
        workbook.SetCellValue(row, 1, rec.AccountName)
        workbook.SetCellValue(row, 2, rec.CurrencyName)
        #workbook.SetCellValue(row, 3, rec.Rate)
        workbook.SetCellValue(row, 3, rec.BeginBalance)
        workbook.SetCellValue(row, 4, rec.Debet)
        workbook.SetCellValue(row, 5, rec.Credit)
        workbook.SetCellValue(row, 6, rec.Total)
        workbook.SetCellValue(row, 7, rec.EndBalance)
        LastCurrency = rec.CurrencyName

        Currencies[rec.CurrencyName]['TotalBegin'] += rec.BeginBalance
        Currencies[rec.CurrencyName]['TotalCredit'] += rec.Credit
        Currencies[rec.CurrencyName]['TotalDebet'] += rec.Debet
        Currencies[rec.CurrencyName]['TotalEnd'] += rec.EndBalance
        
        row += 1
        i += 1
      # end while

      if LastCurrency != '' :
        workbook.SetCellValue(row, 1, 'TOTAL VALUTA KAS/BANK ' + LastCurrency )
        workbook.SetCellValue(row, 2, '')
        #workbook.SetCellValue(row, 3, '')
        workbook.SetCellValue(row, 3, Currencies[LastCurrency]['TotalBegin'])
        workbook.SetCellValue(row, 4, Currencies[LastCurrency]['TotalDebet'])
        workbook.SetCellValue(row, 5, Currencies[LastCurrency]['TotalCredit'])
        workbook.SetCellValue(row, 6, Currencies[LastCurrency]['TotalDebet'] - Currencies[LastCurrency]['TotalCredit'])
        workbook.SetCellValue(row, 7, Currencies[LastCurrency]['TotalEnd'])
      # endif
      
      workbook.SaveAs(filename)

    finally:
      workbook = None

    app.ShellExecuteFile(filename)


