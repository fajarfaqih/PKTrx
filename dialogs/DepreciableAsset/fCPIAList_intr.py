class fCIAList:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    self.FormView = None
    
  def Show(self):

    self.uipData.Edit()
    self.uipData.IsAllCPIA = 'T'
    
    self.ShowCPIAData()
    self.FormContainer.Show()

  def ViewDetail(self,sender):
    self.ViewData()
    
  def ViewData(self):
    if self.FormView == None :
      form = self.app.CreateForm(
          'DepreciableAsset/fCPIAView',
          'DepreciableAsset/fCPIAView',
           0, None, None)
      self.FormView = form
    else:
      form = self.FormView
    # end if
    AccountNo = self.uipCPIA.AccountNo
    form.Show(AccountNo)

  def IsAllCPIAClick(self,sender):
    lsControl = ['LAccount','LCPIACategory','BeginDate','EndDate']
    for controlname in lsControl :
      self.form.GetPanelByName('pFilter').GetControlByName(controlname).Enabled = not sender.Checked


  def ExportExcelClick(self,sender):
    self.ShowCPIAData(1)
    
  def FilterClick(self,sender):
    self.uipCPIA.ClearData()
    self.ShowCPIAData()

  def ShowCPIAData(self,mode = 0):
    app = self.app
    form = self.form
    uipData = self.uipData

    IsAllCPIA = uipData.IsAllCPIA
    Account_Code = uipData.GetFieldValue('LAccount.Account_Code') or ''
    CPIACatId = uipData.GetFieldValue('LCPIACategory.CPIACatId') or 0
    BeginDate = uipData.BeginDate
    EndDate = uipData.EndDate

    BranchCode = self.uipData.BranchCode

    param = self.app.CreateValues(
     ['IsAllCPIA',IsAllCPIA],
     ['BranchCode',BranchCode],
     ['CPIACatId',CPIACatId],
     ['Account_Code',Account_Code],
     ['BeginDate',BeginDate],
     ['EndDate',EndDate],
    )

    if mode == 0 :
      self.form.SetDataWithParameters(param)
    else:
      filename = self.oPrint.ConfirmDestinationPath(app,'xls')
      if filename in ['',None] : return

      ph = self.form.CallServerMethod("GetCPIAList", param)

      status = ph.FirstRecord
      if status.Is_Err : raise 'PERINGATAN',status.Err_Message

      workbook = self.oPrint.OpenExcelTemplate(app,'tplCPIAList.xls')
      workbook.ActivateWorksheet('data')
      try:
        workbook.SetCellValue(2, 3, status.BranchName)
        if IsAllCPIA == 'F' :
          workbook.SetCellValue(3, 3, status.PeriodStr)

          CPIACatName = uipData.GetFieldValue('LCPIACategory.CPIACatName') or ''
          if CPIACatName != '' :
            workbook.SetCellValue(4, 3, CPIACatName)
          
          Account_Code = uipData.GetFieldValue('LAccount.Account_Code') or ''
          Account_Name = uipData.GetFieldValue('LAccount.Account_Name') or ''
          if Account_Code != '' :
            workbook.SetCellValue(5, 3,  '%s - %s ' % (Account_Code,Account_Name))

        ds = ph.packet.CPIAList
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 8

          workbook.SetCellValue(row, 1, str(i+1))
          workbook.SetCellValue(row, 2, rec.AccountNo)
          workbook.SetCellValue(row, 3, rec.AccountName)
          workbook.SetCellValue(row, 4, rec.NilaiAwal)
          workbook.SetCellValue(row, 5, rec.OpeningDate)
          workbook.SetCellValue(row, 6, rec.TransactionNo)
          workbook.SetCellValue(row, 7, rec.CostAccountNo)
          workbook.SetCellValue(row, 8, rec.CostAccountName)
          workbook.SetCellValue(row, 9, rec.CPIACatName)

          i += 1
        # end of while


        workbook.SaveAs(filename)
        app.ShellExecuteFile(filename)

      finally:
        # close
        workbook = None

