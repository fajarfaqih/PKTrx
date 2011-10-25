class fBudgetEdit:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.BudgetId = 0

  def FormOnShow(self,sender):
    self.pBudget_BudgetCode.SetFocus()
    
  def GetData(self,BudgetId):
    self.uipBudget.ClearData()

    ph = self.app.CreateValues(
               ['BudgetId', BudgetId],
    )
    self.form.SetDataWithParameters(ph)

    if self.FormContainer.Show() == 1:
      #self.BudgetId = self.uipBudget.BudgetId
      return 1
    else:
      return 0
      
  def AmountOnExit(self,sender):
    uipBudget = self.uipBudget
    uipBudget.Edit()
    uipBudget.TotalAmount = 0.0
    for i in range(1,13):
      uipBudget.TotalAmount += uipBudget.GetFieldValue('Amount' + str(i)) or 0.0
      
  def SaveClick(self,sender):
    self.form.CommitBuffer()
    ph =  self.form.CallServerMethod('SimpanData',self.form.GetDataPacket())
    
    rec = ph.FirstRecord
    if rec.Is_Err : raise 'PERINGATAN',rec.Err_Message

    self.app.ShowMessage('Data budget berhasil disimpan')
    sender.ExitAction = 1
    
    
    
