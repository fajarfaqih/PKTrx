class fBudgetReport:
  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  def Show(self):
    uipFilter = self.uipFilter
    uipFilter.Edit()
    uipFilter.IsAllOwner = 'F'

    IsHeadOffice = (uipFilter.BranchCode == uipFilter.HeadOfficeCode)

    self.pFilter_LBranch.enabled = IsHeadOffice
    self.MasterBranchCode = ''

    if not IsHeadOffice :
      uipFilter.MasterBranchCode = uipFilter.BranchCode

    uipFilter.SetFieldValue('LBranch.BranchCode', uipFilter.BranchCode)
    uipFilter.SetFieldValue('LBranch.BranchName', uipFilter.BranchName)
    
    self.FormContainer.Show()

  def AllOwnerOnClick(self,sender):
    if sender.Checked != 0 :
      self.uipFilter.SetFieldValue('LBudgetOwner.OwnerCode','')
      self.uipFilter.SetFieldValue('LBudgetOwner.OwnerName','')

    self.pFilter_LBudgetOwner.enabled = (sender.Checked == 0)
    
  def bViewHistClick(self, sender):
    self.ViewHistTransaction(1)

  def bExportExcelClick(self,sender):
    filename = self.oPrint.ConfirmDestinationPath(self.app,'xls')
    if filename in ['',None] : return
    self.ViewHistTransaction(2,filename)

  def ViewHistTransaction(self,mode,filename=None):
    app = self.app
    uipFilter = self.uipFilter
    OwnerId = uipFilter.GetFieldValue('LBudgetOwner.OwnerId') or 0

    BranchCode = uipFilter.GetFieldValue("LBranch.BranchCode") or ''

    if BranchCode == '' :
      raise 'Peringatan','Pilih Cabang terlebih dahulu'

    if uipFilter.BeginDate > uipFilter.EndDate :
       raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'
       
    if uipFilter.IsAllOwner == 'F' and OwnerId in [None , 0 ]:
      raise 'PERINGATAN' ,'Anda belum memilih pemilik anggaran'
    
    self.uipTransaction.ClearData()

    ph = self.FormObject.CallServerMethod(
      'GetHistTransaction',
      self.app.CreateValues(
        ['BranchCode', BranchCode],
        ['OwnerId' , OwnerId ],
        ['IsAllOwner' , uipFilter.IsAllOwner],
        ['BeginDate', uipFilter.BeginDate],
        ['EndDate', uipFilter.EndDate],
      )
    )

    rec = ph.FirstRecord

    ds = ph.packet.histori
    if mode == 1 :
      #self.uipFilter.BeginningBalance = ph.FirstRecord.BeginningBalance
      
      uipTran = self.uipTransaction
      uipTran.ClearData()

      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        uipTran.Append()

        uipTran.OwnerName = rec.OwnerName
        uipTran.BudgetCode = rec.BudgetCode
        uipTran.GroupName = rec.GroupName
        uipTran.ItemName = rec.ItemName
        uipTran.TransactionItemId = rec.TransactionItemId
        uipTran.TransactionDate   = rec.TransactionDate
        uipTran.TransactionCode   = rec.TransactionType
        uipTran.Amount = rec.Amount
        uipTran.AmountEkuivalen = rec.AmountEkuivalen
        uipTran.CurrencyName = rec.CurrencyName
        uipTran.ReferenceNo       = rec.ReferenceNo
        uipTran.Description       = rec.Description
        uipTran.Inputer           = rec.Inputer
        uipTran.Rate = rec.Rate
        uipTran.CurrencyName = rec.CurrencyName
        uipTran.TransactionNo = rec.NoTransaksi
        

        i += 1
      # end of while

      uipTran.First()

    else:

      workbook = self.oPrint.OpenExcelTemplate(app,'tplHistTransBudgetReport.xls')
      workbook.ActivateWorksheet('data')

      try:
        workbook.SetCellValue(2, 2, rec.Tanggal)
        #workbook.SetCellValue(2, 2, rec.TotalAmount)
        
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 5
          workbook.SetCellValue(row, 1, rec.OwnerName)
          workbook.SetCellValue(row, 2, rec.BudgetCode)
          workbook.SetCellValue(row, 3, rec.GroupName)
          workbook.SetCellValue(row, 4, rec.ItemName)
          workbook.SetCellValue(row, 5, rec.TransactionDateStr)
          workbook.SetCellValue(row, 6, rec.Amount)
          workbook.SetCellValue(row, 7, rec.CurrencyName)
          workbook.SetCellValue(row, 8, rec.AmountEkuivalen)
          workbook.SetCellValue(row, 9, rec.TransactionType)
          workbook.SetCellValue(row, 10, rec.Description)
          workbook.SetCellValue(row, 11, rec.NoTransaksi)
          workbook.SetCellValue(row, 12, rec.Inputer)
          workbook.SetCellValue(row, 13, rec.ReferenceNo)

          i += 1
        # end of while

        workbook.SaveAs(filename)
      finally:
        # close
        workbook = None
        
      app.ShellExecuteFile(filename)
