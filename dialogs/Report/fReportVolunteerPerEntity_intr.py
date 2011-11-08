MAP_ENTITY={
  0 : 'Seluruhnya',
  1 : 'Zakat',
  2 : 'Infaq',
  3 : 'Wakaf',
  4 : 'Amil',
  5 : 'Non Halal',
}

class fReportVolunteerPerEntity:
  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  def Show(self):
    self.uipVolunteer.Edit()
    self.uipVolunteer.FundEntity = 0
    return self.FormContainer.Show()

  def bViewHistClick (self, sender):
    self.ViewHistTransaction(1)

  def LVolunteerAfterLookup(self,sender,linkUI):
    uipVolunteer = self.uipVolunteer
    uipVolunteer.Edit()
    uipVolunteer.VolunteerName = uipVolunteer.GetFieldValue('LVolunteer.VolunteerName') or ''
    uipVolunteer.HomePhone = uipVolunteer.GetFieldValue('LVolunteer.HomePhone') or ''
    uipVolunteer.HomeAddress = uipVolunteer.GetFieldValue('LVolunteer.HomeAddress') or ''
    uipVolunteer.VolunteerId = uipVolunteer.GetFieldValue('LVolunteer.VolunteerId')
    self.form.GetPanelByName('pVolunteer').GetControlByName('edAddress').Text = uipVolunteer.GetFieldValue('LVolunteer.HomeAddress') or ''


  def bExportClick(self,sender):
    app = self.app

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename == '' : return

    self.ViewHistTransaction(2,filename)

  def ViewHistTransaction(self,mode,filename=None):
    app = self.app
    uipVolunteer = self.uipVolunteer
    self.FormObject.CommitBuffer()
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['VolunteerId', uipVolunteer.GetFieldValue('LVolunteer.VolunteerId')],
        ['BeginDate', uipVolunteer.BeginDate],
        ['EndDate', uipVolunteer.EndDate],
        ['FundEntity',uipVolunteer.FundEntity]
      )
    )



    ds = ph.packet.histori
    if mode == 1 :
      self.uipVolunteer.BeginningBalance = ph.FirstRecord.BeginningBalance
      
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
      workbook = self.oPrint.OpenExcelTemplate(app,'tplHistTransVolunteer.xls')
      workbook.ActivateWorksheet('data')
      try:
        status = ph.FirstRecord
        #workbook.SetCellValue(1, 2, uipVolunteer.GetFieldValue('LProject.LProject.ProductName'))
        workbook.SetCellValue(2, 2, uipVolunteer.VolunteerName)
        workbook.SetCellValue(3, 2, MAP_ENTITY[uipVolunteer.FundEntity])
        workbook.SetCellValue(4, 2, status.PeriodStr)
        workbook.SetCellValue(5, 2, status.BeginningBalance)
        workbook.SetCellValue(6, 2, status.TotalDebet)
        workbook.SetCellValue(7, 2, status.TotalCredit)
        workbook.SetCellValue(8, 2, status.EndBalance)

        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 11
          #workbook.SetCellValue(row, 1, rec.TransactionItemId)
          workbook.SetCellValue(row, 1, rec.TransactionDateStr)
          workbook.SetCellValue(row, 2, rec.TransactionType)
          workbook.SetCellValue(row, 3, MAP_ENTITY[rec.FundEntity])
          workbook.SetCellValue(row, 4, rec.Debet)
          workbook.SetCellValue(row, 5, rec.Kredit)
          workbook.SetCellValue(row, 6, str(rec.PercentageOfAmil) + ' %')
          workbook.SetCellValue(row, 7, rec.AmilAmount)
          workbook.SetCellValue(row, 8, rec.Description)
          workbook.SetCellValue(row, 9, rec.Inputer)
          workbook.SetCellValue(row, 10, rec.NoTransaksi)
          workbook.SetCellValue(row, 11, rec.ReferenceNo)
          i += 1
        # end of while

        workbook.SaveAs(filename)
      finally:
        # close
        workbook = None

      app.ShellExecuteFile(filename)
      
