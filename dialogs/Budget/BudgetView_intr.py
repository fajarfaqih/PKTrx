class fBudgetList:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.userapp = self.app.UserAppObject

  def Show(self):
    return self.FormContainer.Show()

  def GetBudgetId(self):
    return self.uipBudgetItem.BudgetId or 0

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


