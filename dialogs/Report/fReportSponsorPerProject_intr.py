class fReportSponsorPerProject:
  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    self.fSearchDonor = None

  def Show(self):
    self.uipSponsor.Edit()
    self.uipSponsor.IsAllProject = 'F'
    return self.FormContainer.Show()

  def bViewHistClick (self, sender):
    self.ViewHistTransaction(1)

  def AllProjectOnClick(self,sender):
    LProject = self.form.GetControlByName('pSelectTransaction.LProject')
    LProject.Enabled = not (sender.Checked)
    if sender.Checked :
      self.uipSponsor.Edit()
      self.uipSponsor.SetFieldValue('LProject.LProjectAccount.AccountNo','')
      self.uipSponsor.SetFieldValue('LProject.LProjectAccount.AccountName','')
    
  def LSponsorAfterLookup(self,sender,linkUI):
    uipSponsor = self.uipSponsor
    uipSponsor.Edit()
    uipSponsor.SponsorName = uipSponsor.GetFieldValue('LSponsor.Name')
    uipSponsor.SponsorDescription = uipSponsor.GetFieldValue('LSponsor.Description')
    uipSponsor.SponsorAddress = uipSponsor.GetFieldValue('LSponsor.Address')
    uipSponsor.SponsorId = uipSponsor.GetFieldValue('LSponsor.SponsorId')

  def SponsorClick(self,sender):
    if self.fSearchDonor == None :
      fSearch = self.app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
      self.fSearchDonor = fSearch
    else :
      fSearch = self.fSearchDonor

    if fSearch.GetDonorData():
      uipSponsor = self.uipSponsor
      uipSponsor.Edit()

      uipSponsor.SponsorId = fSearch.DonorIntId
      uipSponsor.SponsorName = fSearch.DonorName
      #uipSponsor.SponsorDescription = uipSponsor.GetFieldValue('LSponsor.Description')
      uipSponsor.SponsorAddress = fSearch.Address

  def bExportClick(self,sender):
    app = self.app

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename == '' : return

    self.ViewHistTransaction(2,filename)

  def ViewHistTransaction(self,mode,filename=None):
    app = self.app
    uipSponsor = self.uipSponsor
    
    #if uipSponsor.GetFieldValue('LSponsor.SponsorId') in [0,'',None]:
    if uipSponsor.SponsorId in [0,'',None]:
      raise 'PERINGATAN','Anda belum memilih sponsor'

    #if uipSponsor.GetFieldValue('LProject.ProjectSponsorId') in [0,'',None]:
    #  raise 'PERINGATAN','Anda belum memilih project'
      
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['SponsorId', uipSponsor.SponsorId],
        ['BeginDate', uipSponsor.BeginDate],
        ['EndDate', uipSponsor.EndDate],
        ['IsAllProject',uipSponsor.IsAllProject],
        ['ProjectSponsorId',uipSponsor.GetFieldValue('LProject.ProjectSponsorId') or ''],
        ['AccountNo',uipSponsor.GetFieldValue('LProject.LProjectAccount.AccountNo') or ''],
      )
    )



    ds = ph.packet.histori
    if mode == 1 :
      self.uipSponsor.BeginningBalance = ph.FirstRecord.BeginningBalance
      
      uipTran = self.uipTransaction
      uipTran.ClearData()

      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        uipTran.Append()

        uipTran.TransactionItemId = rec.TransactionItemId
        uipTran.TransactionDate   = rec.TransactionDate
        uipTran.TransactionCode   = rec.TransactionType
        uipTran.Debet = rec.Debet
        uipTran.Kredit = rec.Kredit
        uipTran.ReferenceNo       = rec.ReferenceNo
        uipTran.Description       = rec.Description
        uipTran.Inputer           = rec.Inputer

        i += 1
      # end of while

      uipTran.First()

    else:
      rec = ph.FirstRecord
      workbook = self.oPrint.OpenExcelTemplate(app,'tplHistTransSponsor.xls')
      workbook.ActivateWorksheet('data')
      try:

        workbook.SetCellValue(2, 2, uipSponsor.SponsorName)
        workbook.SetCellValue(3, 2, uipSponsor.GetFieldValue('LProject.LProjectAccount.AccountName'))
        workbook.SetCellValue(4, 2, rec.PeriodStr)
        workbook.SetCellValue(5, 2, rec.BeginningBalance)
        workbook.SetCellValue(6, 2, rec.TotalDebet)
        workbook.SetCellValue(7, 2, rec.TotalCredit)
        workbook.SetCellValue(8, 2, rec.EndBalance)
        
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 11
          #workbook.SetCellValue(row, 1, rec.TransactionItemId)
          workbook.SetCellValue(row, 1, rec.TransactionDateStr)
          workbook.SetCellValue(row, 2, rec.TransactionType)
          workbook.SetCellValue(row, 3, rec.Debet)
          workbook.SetCellValue(row, 4, rec.Kredit)
          workbook.SetCellValue(row, 5, str(rec.PercentageOfAmil) + ' %')
          workbook.SetCellValue(row, 6, rec.AmilAmount)
          workbook.SetCellValue(row, 7, rec.Description)
          workbook.SetCellValue(row, 8, rec.Inputer)
          workbook.SetCellValue(row, 9, rec.NoTransaksi)
          i += 1
        # end of while

        workbook.SaveAs(filename)
        #self.app.ShowMessage('File telah berhasil di generate di :\n' + filename)
      finally:
        # close
        workbook = None

      app.ShellExecuteFile(filename)
