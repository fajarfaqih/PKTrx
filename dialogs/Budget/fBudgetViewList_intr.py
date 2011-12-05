class fBudgetViewList:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.userapp = self.app.UserAppObject
    self.fViewDetail = None
    self.fViewTran = None
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
        
  def Show(self):
    self.FillPeriodYear()
    uipBudget = self.uipBudget

    uipBudget.Edit()
    uipBudget.IsAllOwner = 'F'
    IsHeadOffice = (uipBudget.BranchCode == uipBudget.HeadOfficeCode)
    self.pBudget_LBranch.enabled = IsHeadOffice
    self.MasterBranchCode = ''

    if not IsHeadOffice :
      uipBudget.MasterBranchCode = uipBudget.BranchCode
      
    uipBudget.SetFieldValue('LBranch.BranchCode', uipBudget.BranchCode)
    uipBudget.SetFieldValue('LBranch.BranchName', uipBudget.BranchName)
    
    return self.FormContainer.Show()

  def AllOnCheck(self,sender):
    self.form.GetPanelByName('pBudget').GetControlByName('LBudgetOwner').Enabled = not sender.Checked
    
    uipBudget = self.uipBudget
    if sender.Checked :
      uipBudget.SetFieldValue('LBudgetOwner.OwnerCode','')
      uipBudget.SetFieldValue('LBudgetOwner.OwnerName','')
    

  def GetBudgetId(self):
    return self.uipBudgetItem.BudgetId or 0

  def FillPeriodYear(self):
    ph = self.app.CreateValues()
    rph = self.form.CallServerMethod('GetPeriodYear',ph)

    dsPeriod = rph.packet.perioddata

    i= 0
    tempItems = []
    tempValues = []
    while i < dsPeriod.RecordCount:
      recPeriod = dsPeriod.GetRecord(i)
      tempItems.append(str(recPeriod.periodvalue))
      tempValues.append(str(recPeriod.periodid))
      i += 1

    self.pBudget_cbPeriod.Items = '\r'.join(tempItems)
    self.pBudget_cbPeriod.Values = '\r'.join(tempValues)

  def UpdateAmount(self,RevisionAmount):
    self.uipBudgetItem.Edit()
    self.uipBudgetItem.Amount = RevisionAmount
    
  def LBudgetPeriodAfterClick(self,ctlLink,Link):
    uipBudget = self.uipBudget
    uipBudget.Edit()
    uipBudget.Bulan = uipBudget.GetFieldValue("LBudgetPeriod.PeriodValue")
    uipBudget.Tahun = uipBudget.GetFieldValue("LBudgetPeriod.LParent.PeriodValue")


  def ExcelClick(self,sender):
    app = self.app
    uipBudget = self.uipBudget
    
    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return

    OwnerId = uipBudget.GetFieldValue("LBudgetOwner.OwnerId") or 0

    rph = self.GetDataBudget()
    
    status = rph.FirstRecord
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message
    

    workbook = self.oPrint.OpenExcelTemplate(app,'tplBudgetData.xls')
    workbook.ActivateWorksheet('Data')
    try :
      workbook.SetCellValue(2, 2, uipBudget.GetFieldValue('LBranch.BranchName'))
      workbook.SetCellValue(3, 2, status.PeriodYear)
      workbook.SetCellValue(4, 2, uipBudget.GetFieldValue("LBudgetOwner.OwnerName"))

      ds = rph.packet.budgetdata
      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        row = i + 8

        workbook.SetCellValue(row, 1, rec.BudgetCode)
        workbook.SetCellValue(row, 2, rec.ItemGroup)
        workbook.SetCellValue(row, 3, rec.ItemName)
        workbook.SetCellValue(row, 4, rec.Amount)
        workbook.SetCellValue(row, 5, rec.Realization)
        workbook.SetCellValue(row, 6, rec.SalvageValue)
        workbook.SetCellValue(row, 7, rec.OwnerName)
        
        i += 1
      # end while

      workbook.SaveAs(filename)

    finally:
      workbook = None

    app.ShellExecuteFile(filename)

  def GetDataBudget(self):
    param = self.GenerateParamForSendToServer()
    rph = self.form.CallServerMethod('GetBudgetData',param)
    
    return rph
    
  def GenerateParamForSendToServer(self):
    uipBudget = self.uipBudget

    OwnerId    = uipBudget.GetFieldValue("LBudgetOwner.OwnerId") or 0
    IsAllOwner = uipBudget.IsAllOwner
    PeriodID   = uipBudget.PeriodID
    BranchCode = uipBudget.GetFieldValue("LBranch.BranchCode") or ''

    # Validation Check
    if BranchCode == '' :
      raise 'Peringatan','Pilih Cabang terlebih dahulu'
      
    if OwnerId == 0 and uipBudget.IsAllOwner == 'F' :
      raise 'Peringatan','Pilih pemilik anggaran terlebih dahulu'

    if PeriodID in [None,0,''] :
      raise 'Peringatan','Pilih periode anggaran terlebih dahulu'
      
      
    # Create DataPacket
    ph = self.app.CreateValues(
          ['BranchCode', BranchCode],
          ['PeriodId', PeriodID],
          ['OwnerId', OwnerId],
          ['IsAllOwner',IsAllOwner]
    )
    
    return ph
    
  def ShowDataClick(self,sender):
    self.uipBudgetItem.ClearData()
    ph = self.GenerateParamForSendToServer()
    self.form.SetDataWithParameters(ph)

  def bSimpanClick(self,sender):
    app = self.app
    form = self.form
    if app.ConfirmDialog('Yakin simpan data ?'):
      form.CommitBuffer()

      resp = form.CallServerMethod('SimpanData',self.FormObject.GetDataPacket())
      
      rec = resp.FirstRecord
      if rec.Is_Err : raise 'PERINGATAN',rec.Err_Message
      
      app.ShowMessage('Data budget telah berhasil disimpan')
      sender.ExitAction = 1

  def NewClick(self,sender):
    if self.fNewBudget == None :
      form = self.app.CreateForm('Budget/fBudgetNew','Budget/fBudgetNew',0,None,None)
      self.fNewBudget = form
    else:
      form = self.fNewBudget

    uipBudget = self.uipBudget
    OwnerId = uipBudget.GetFieldValue("LBudgetOwner.OwnerId") or 0
    PeriodID = uipBudget.PeriodID
    if form.GetNewData(OwnerId,PeriodIDl):
      uipBudgetItem = self.uipBudgetItem
      uipBudgetItem.Append()
      uipBudgetItem.BudgetId = form.uipBudget.BudgetId
      uipBudgetItem.ItemName = form.uipBudget.ItemName
      uipBudgetItem.Amount = form.uipBudget.TotalAmount
      uipBudgetItem.BudgetCode = form.uipBudget.BudgetCode
      
      
  def ViewDetailClick(self,sender):
    BudgetId = self.uipBudgetItem.BudgetId
    if self.fViewDetail == None :
      param = self.app.CreateValues(
               ['BudgetId', BudgetId],
      )
      form = self.app.CreateForm('Budget/fBudgetViewDetail','Budget/fBudgetViewDetail',0,param,None)
      self.fViewDetail = form
    else:
      form = self.fViewDetail

    form.ViewData(BudgetId)

  def ViewTransactionClick(self,sender):
    BudgetId = self.uipBudgetItem.BudgetId
    if self.fViewTran == None :
      param = self.app.CreateValues(
               ['BudgetId', BudgetId],
      )
      form = self.app.CreateForm('Budget/fBudgetViewTransaction','Budget/fBudgetViewTransaction',0,param,None)
      self.fViewTran = form
    else:
      form = self.fViewTran

    form.Show(BudgetId)
    
  def DeleteClick(self,sender):
    app = self.app
    form = self.form
    uipBudgetItem = self.uipBudgetItem
    
    param = app.CreateValues(['BudgetId',uipBudgetItem.BudgetId])
    rph = form.CallServerMethod('DeleteBudget',param)
    
    rec = rph.FirstRecord
    
    if rec.Is_Err : raise 'PERINGATAN',rec.Err_Message
    
    app.ShowMessage('Data telah berhasil dihapus')
    uipBudgetItem.Delete()
    
