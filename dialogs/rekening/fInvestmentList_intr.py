class fInvestmentList:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.FormView = None
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  def Show(self):

    self.uipData.Edit()
    self.uipData.IsAllInvestment = 'T'
    
    self.ShowInvestmentData()
    self.FormContainer.Show()

  def IsAllInvestmentOnClick(self,sender):
    lsControl = ['LInvestmentCategory','BeginDate','EndDate']
    for controlname in lsControl :
      self.form.GetPanelByName('pFilter').GetControlByName(controlname).Enabled = not sender.Checked


  def DetailClick(self,sender):
    self.ViewData()
    
  def ViewData(self):
    if self.FormView == None :
      form = self.app.CreateForm(
          'rekening/fInvestmentView',
          'rekening/fInvestmentView',
           0, None, None)
      self.FormView = form
    else:
      form = self.FormView
    # end if
    #AccountNo = self.qInvestment.GetFieldValue('Investment.Kode_Investasi')
    AccountNo = self.uipInvestment.AccountNo
    form.Show(AccountNo)

  def FilterClick(self,sender):
    self.uipInvestment.ClearData()
    self.ShowInvestmentData()

  def ExportExcelClick(self,sender):
    self.ShowInvestmentData(1)
    
  def ShowInvestmentData(self,mode=0):
    app = self.app
    uipData = self.uipData

    IsAllInvestment = uipData.IsAllInvestment
    InvestmentCatId = uipData.GetFieldValue('LInvestmentCategory.InvestmentCatId') or 0
    BranchCode = uipData.BranchCode
    BeginDate = uipData.BeginDate
    EndDate = uipData.EndDate

    param = self.app.CreateValues(
     ['IsAllInvestment',IsAllInvestment],
     ['BranchCode',BranchCode],
     ['InvestmentCatId',InvestmentCatId],
     ['BeginDate',BeginDate],
     ['EndDate',EndDate],
    )

    if mode == 0 :
      self.form.SetDataWithParameters(param)

    else :
      filename = self.oPrint.ConfirmDestinationPath(app,'xls')
      if filename in ['',None] : return

      ph = self.form.CallServerMethod("GetInvestmentList", param)

      status = ph.FirstRecord
      if status.Is_Err : raise 'PERINGATAN',status.Err_Message

      workbook = self.oPrint.OpenExcelTemplate(app,'tplInvestmentList.xls')
      workbook.ActivateWorksheet('data')
      try:
        workbook.SetCellValue(2, 3, status.BranchName)
        if IsAllInvestment == 'F' :
          workbook.SetCellValue(3, 3, status.PeriodStr)
          CategoryName = uipData.GetFieldValue('LInvestmentCategory.InvestmentCatName') or ''
          if CategoryName != '' :
            workbook.SetCellValue(4, 3,  CategoryName)

        ds = ph.packet.InvestmentList
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 7

          workbook.SetCellValue(row, 1, str(i+1))
          workbook.SetCellValue(row, 2, rec.AccountNo)
          workbook.SetCellValue(row, 3, rec.AccountName)
          workbook.SetCellValue(row, 4, rec.InvesteeName)
          workbook.SetCellValue(row, 5, rec.InvestmentAmount)
          workbook.SetCellValue(row, 6, rec.InvestmentNisbah)
          workbook.SetCellValue(row, 7, rec.OpeningDate)
          workbook.SetCellValue(row, 8, rec.InvestmentCatName)
          workbook.SetCellValue(row, 9, rec.TransactionNo)

          i += 1
        # end of while


        workbook.SaveAs(filename)
        app.ShellExecuteFile(filename)

      finally:
        # close
        workbook = None

