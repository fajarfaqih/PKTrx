Entities = ['Seluruhnya','Zakat','Infaq','Wakaf']

class fCashOutReport:
  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  def Show(self):
    uipFilter = self.uipFilter
    uipFilter.Edit()
    uipFilter.IsAllBranch = 'F'

    # Set Branch Filter
    IsHeadOffice = (uipFilter.BranchCode == uipFilter.HeadOfficeCode)
    self.MasterBranchCode = ''
    if not IsHeadOffice :
      uipFilter.MasterBranchCode = uipFilter.BranchCode
      
    uipFilter.SetFieldValue('LBranch.BranchCode',uipFilter.BranchCode)
    uipFilter.SetFieldValue('LBranch.BranchName',uipFilter.BranchName)

    return self.FormContainer.Show()

  def IsAllBranchOnClick(self,sender):
    self.form.GetPanelByName('pFilter').GetControlByName('LBranch').Enabled = not sender.Checked
    
  def bViewHistClick (self, sender):
    self.ViewHistTransaction(1)

  def bExportClick(self,sender):
    app = self.app

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return
    
    self.ViewHistTransaction(2,filename)

  def ViewHistTransaction(self,mode,filename=None):
    app = self.app
    uipFilter = self.uipFilter
    
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['BeginDate', uipFilter.BeginDate],
        ['EndDate', uipFilter.EndDate],
        ['IsAllBranch',uipFilter.IsAllBranch],
        ['BranchCode',uipFilter.GetFieldValue('LBranch.BranchCode') or ''],
      )
    )

    ds = ph.packet.ReportData

    if ds.RecordCount <= 0 :
      app.ShowMessage('Tidak ada transaksi')
      return
    
    if mode == 1 :
      #uipData.BeginningBalance = ph.FirstRecord.BeginningBalance
      
      uipTran = self.uipTransaction
      uipTran.ClearData()

      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        uipTran.Append()

        uipTran.TransactionItemId = rec.TransactionItemId
        uipTran.TransactionDate   = rec.TransactionDateStr
        uipTran.AccountNo   = rec.AccountNo
        uipTran.AccountName   = rec.AccountName
        #uipTran.TransactionCode   = rec.TransactionCode
        #uipTran.MutationType      = rec.MutationType
        uipTran.Amount            = rec.Amount
        uipTran.ReferenceNo       = rec.ReferenceNo
        uipTran.Description       = rec.Description
        uipTran.Inputer           = rec.Inputer
        uipTran.BranchName        = rec.BranchName

        i += 1
      # end of while

      uipTran.First()

    else:
      workbook = self.oPrint.OpenExcelTemplate(app,'tplCashOutReport.xls')
      workbook.ActivateWorksheet('data')
      try:
        NamaCabang = ph.FirstRecord.NamaCabang
        PeriodStr = ph.FirstRecord.PeriodStr
        TotalAmount = ph.FirstRecord.TotalAmount

        if uipFilter.IsAllBranch == 'T' :
          workbook.SetCellValue(2, 3, NamaCabang)
          
        workbook.SetCellValue(3, 3, PeriodStr)
        workbook.SetCellValue(4, 3, TotalAmount)


        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 7
          
          workbook.SetCellValue(row, 1, str(i+1))
          workbook.SetCellValue(row, 2, rec.TransactionDateStr)
          workbook.SetCellValue(row, 3, rec.AccountNo)
          workbook.SetCellValue(row, 4, rec.AccountName)
          workbook.SetCellValue(row, 5, rec.Amount)
          workbook.SetCellValue(row, 6, rec.Description)
          workbook.SetCellValue(row, 7, rec.ReferenceNo)
          workbook.SetCellValue(row, 8, rec.Inputer)
          workbook.SetCellValue(row, 9, rec.BranchName)

          i += 1
        # end of while

        
        workbook.SaveAs(filename)
        app.ShellExecuteFile(filename)
        
      finally:
        # close
        workbook = None
