class fSearchInvestManager:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    
  def ShowData(self):
    self.uipInvestManager.First()
    st = self.FormContainer.Show()
    if st == 1:
      return 1
    else:
      return 0

  def GridDoubleClick(self,sender):
    self.bSelectClick(self.pAction_bSelect)
    
  def bSelectClick(self,sender):
    sender.ExitAction = 1
    
  def NameOnExit(self,sender):
    Nama = self.uipFilter.Nama or ''
    if Nama == '': return
    self.GetDataManager(Nama)
    
  def GetDataManager(self,NameFilter):
    app = self.app
    form = self.form
    uipManager = self.uipInvestManager
    
    ph = form.CallServerMethod('GetDataManager',app.CreateValues(['NameFilter',NameFilter]))
    
    status = ph.FirstRecord
    
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message
    
    dsManager = ph.packet.ListManager
    uipManager.ClearData()
    
    TotalRecord = dsManager.RecordCount
    i = 0
    while i < TotalRecord:
      rec = dsManager.GetRecord(i)
      uipManager.Append()
      
      uipManager.ManagerId = rec.ManagerId
      uipManager.ManagerName = rec.ManagerName
      i += 1
    # end while
    uipManager.First()

