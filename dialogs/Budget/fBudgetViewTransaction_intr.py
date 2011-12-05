class fBudgetViewTransaction:
  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  def Show(self,BudgetId):
    #self.uipBudget.Edit()
    #self.uipBudget.IsAllProject = 'F'
    
    ph = self.app.CreateValues(
               ['BudgetId', BudgetId],
    )
    self.form.SetDataWithParameters(ph)
    self.ViewHistTransaction(1)
    
    return self.FormContainer.Show()

  def bViewHistClick (self, sender):
    self.ViewHistTransaction(1)

  def bExportExcelClick(self,sender):
    filename = self.oPrint.ConfirmDestinationPath(self.app,'xls')
    if filename in ['',None] : return
    self.ViewHistTransaction(2,filename)

  def ViewHistTransaction(self,mode,filename=None):
    app = self.app
    uipBudget = self.uipBudget
    
    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['BudgetId', uipBudget.BudgetId],
        ['BeginDate', uipBudget.BeginDate],
        ['EndDate', uipBudget.EndDate],
      )
    )

    rec = ph.FirstRecord

    ds = ph.packet.histori
    if mode == 1 :
      #self.uipBudget.BeginningBalance = ph.FirstRecord.BeginningBalance
      
      uipTran = self.uipTransaction
      uipTran.ClearData()

      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        uipTran.Append()

        uipTran.TransactionItemId = rec.TransactionItemId
        uipTran.TransactionDate   = rec.TransactionDate
        uipTran.TransactionCode   = rec.TransactionType
        uipTran.Amount = rec.Amount
        uipTran.ReferenceNo       = rec.ReferenceNo
        uipTran.Description       = rec.Description
        uipTran.Inputer           = rec.Inputer
        uipTran.BudgetTransactionType = rec.BudgetTransactionType

        i += 1
      # end of while

      uipTran.First()

    else:

      workbook = self.oPrint.OpenExcelTemplate(app,'tplHistTransBudget.xls')
      workbook.ActivateWorksheet('data')

      try:
        workbook.SetCellValue(2, 2, uipBudget.Tahun)
        workbook.SetCellValue(3, 2, uipBudget.BudgetCode)
        workbook.SetCellValue(4, 2, uipBudget.ItemGroup)
        workbook.SetCellValue(5, 2, uipBudget.ItemName)
        workbook.SetCellValue(6, 2, rec.Tanggal)
        workbook.SetCellValue(7, 2, rec.TotalAmount)
        
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 10
          #workbook.SetCellValue(row, 1, rec.TransactionItemId)
          workbook.SetCellValue(row, 1, rec.TransactionDateStr)
          workbook.SetCellValue(row, 2, rec.TransactionType)
          workbook.SetCellValue(row, 3, rec.Amount)
          workbook.SetCellValue(row, 4, rec.BudgetTransactionType)
          workbook.SetCellValue(row, 5, rec.Description)
          workbook.SetCellValue(row, 6, rec.Inputer)
          workbook.SetCellValue(row, 7, rec.NoTransaksi)
          i += 1
        # end of while

        workbook.SaveAs(filename)
      finally:
        # close
        workbook = None
        
      app.ShellExecuteFile(filename)
