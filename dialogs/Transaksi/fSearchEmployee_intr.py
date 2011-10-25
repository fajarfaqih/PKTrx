class fSearchEmployee:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    
  def ShowData(self):
    self.uipEmployee.First()
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
    self.GetDataEmployee(Nama)
    
  def GetDataEmployee(self,NameFilter):
    app = self.app
    form = self.form
    uipEmployee = self.uipEmployee
    
    ph = form.CallServerMethod('GetDataEmployee',app.CreateValues(['NameFilter',NameFilter]))
    
    status = ph.FirstRecord
    
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message
    
    dsEmployee = ph.packet.ListEmployee
    uipEmployee.ClearData()
    
    TotalRecord = dsEmployee.RecordCount
    i = 0
    while i < TotalRecord:
      rec = dsEmployee.GetRecord(i)
      uipEmployee.Append()
      
      uipEmployee.EmployeeId = rec.EmployeeId
      uipEmployee.EmployeeName = rec.EmployeeName
      i += 1
    # end while
    uipEmployee.First()

