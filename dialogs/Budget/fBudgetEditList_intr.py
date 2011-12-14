class fBudgetEditList:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.userapp = self.app.UserAppObject
    self.fNewBudget = None
    self.fEditBudget = None

  def Show(self):
    self.FillPeriodYear()
    return self.FormContainer.Show()

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

    
  def PilihPeriodeClick(self,sender):
    uipBudget = self.uipBudget
    
    OwnerId = uipBudget.GetFieldValue("LBudgetOwner.OwnerId") or 0
    if OwnerId == 0 : raise 'Peringatan','Pilih pemilik anggaran terlebih dahulu'
    app = self.app
    ph = app.CreateValues(['OwnerId',OwnerId])
    fSelect = app.CreateForm('Budget/fSelectPeriodRevision', 'fSelectPeriodRevision', 0, ph, None)
    if fSelect.LookUp():
      uipBudget = self.uipBudget
      uipBudget.Edit()
      uipBudget.Bulan = fSelect.Bulan
      uipBudget.Tahun = fSelect.Tahun
      uipBudget.PeriodID = fSelect.PeriodID
      
      ph = self.app.CreateValues(
               ['PeriodId', uipBudget.PeriodID],
               ['OwnerId', OwnerId]
             )
      self.form.SetDataWithParameters(ph)
      
    # end if

  def ShowDataClick(self,sender):
    uipBudget = self.uipBudget

    OwnerId = uipBudget.GetFieldValue("LBudgetOwner.OwnerId") or 0
    if OwnerId == 0 : raise 'Peringatan','Pilih pemilik anggaran terlebih dahulu'
      #uipBudget.PeriodID = fSelect.PeriodID

    ph = self.app.CreateValues(
          ['PeriodId', uipBudget.PeriodID],
          ['OwnerId', OwnerId]
    )
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

    if OwnerId == 0 :
      raise 'PERINGATAN','Pilih Dahulu Pemilik Budget'

    if PeriodID == 0 :
      raise 'PERINGATAN','Pilih Dahulu Periode Anggaran'
    
    if form.GetNewData(OwnerId,PeriodID):
      uipBudgetItem = self.uipBudgetItem
      uipBudgetItem.Append()
      uipBudgetItem.BudgetId = form.uipBudget.BudgetId
      uipBudgetItem.ItemName = form.uipBudget.ItemName
      uipBudgetItem.Amount = form.uipBudget.TotalAmount
      uipBudgetItem.BudgetCode = form.uipBudget.BudgetCode
      
      uipBudgetItem.ItemGroup = form.GroupName # form.uipBudget.GetFieldValue('LGroupItem.BudgetItemName')
      
      
  def EditClick(self,sender):
    BudgetId = self.uipBudgetItem.BudgetId or 0

    if BudgetId == 0 :
      raise 'PERINGATAN','Silahkan pilih dahulu anggaran yang akan diubah'
    
    if self.fEditBudget == None :
      param = self.app.CreateValues(
               ['BudgetId', BudgetId],
      )
      form = self.app.CreateForm('Budget/fBudgetEdit','Budget/fBudgetEdit',0,param,None)
      self.fEditBudget = form
    else:
      form = self.fEditBudget

    if form.GetData(BudgetId):
      uipBudgetItem = self.uipBudgetItem
      uipBudgetItem.Edit()
      uipBudgetItem.BudgetId = form.uipBudget.BudgetId
      uipBudgetItem.ItemName = form.uipBudget.ItemName
      uipBudgetItem.Amount = form.uipBudget.TotalAmount
      uipBudgetItem.BudgetCode = form.uipBudget.BudgetCode
    
  def DeleteClick(self,sender):
    app = self.app
    form = self.form
    uipBudgetItem = self.uipBudgetItem

    BudgetId = uipBudgetItem.BudgetId or 0
    if BudgetId == 0 :
      raise 'PERINGATAN','Silahkan pilih dahulu anggaran yang akan dihapus'

    param = app.CreateValues(['BudgetId',BudgetId])
    
    rph = form.CallServerMethod('DeleteBudget',param)
    
    rec = rph.FirstRecord
    
    if rec.Is_Err : raise 'PERINGATAN',rec.Err_Message
    
    app.ShowMessage('Data telah berhasil dihapus')
    uipBudgetItem.Delete()
    
