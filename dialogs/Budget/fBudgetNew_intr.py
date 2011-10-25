class fBudgetNew:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.BudgetId = 0

  def FormOnShow(self,sender):
    self.pBudget_BudgetCode.SetFocus()

  def InputGroupTypeChange(self,sender):
    self.pBudget_LGroupItem.Visible = (sender.ItemIndex == 0)
    self.pBudget_NewGroupName.Visible = (sender.ItemIndex == 1)

  def GetNewData(self,OwnerId,PeriodId):
    self.uipBudget.ClearData()
    
    params = self.app.CreateValues(
      ['OwnerId',OwnerId],['PeriodId',PeriodId])
    self.form.SetDataWithParameters(params)

    self.uipBudget.Edit()
    self.uipBudget.InputGroupType = 'X'
    self.pBudget_NewGroupName.Visible = 0
    
    st = self.FormContainer.Show()

    if st == 1:
      self.BudgetId = self.uipBudget.BudgetId
      if self.uipBudget.InputGroupType == 'X' :
        self.GroupName = self.uipBudget.GetFieldValue('LGroupItem.BudgetItemDescription')
      else:
        self.GroupName = self.uipBudget.NewGroupName
        
      return 1
    else:
      return 0
      
  def AmountOnExit(self,sender):
    uipBudget = self.uipBudget
    uipBudget.TotalAmount = 0.0
    for i in range(1,13):
      uipBudget.TotalAmount += uipBudget.GetFieldValue('Amount' + str(i)) or 0.0
      
  def SaveClick(self,sender):
    self.form.CommitBuffer()
    ph =  self.form.CallServerMethod('SimpanData',self.form.GetDataPacket())
    
    rec = ph.FirstRecord
    if rec.Is_Err :
      raise 'PERINGATAN',rec.Err_Message

    self.app.ShowMessage('Data budget berhasil disimpan')
    self.uipBudget.Edit()
    self.uipBudget.BudgetId = rec.BudgetId
    sender.ExitAction = 1
    
    
    
