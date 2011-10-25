class fSelectBudgetItem :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.ItemCode = None
    self.ItemName = None

  def GetItem(self,OwnerId,PeriodId):
    uipBudgetItem = self.uipBudgetItem
      
    ph = self.app.CreateValues(['OwnerId', OwnerId], ['PeriodId', PeriodId])
    self.FormObject.SetDataWithParameters(ph)
    self.uipBudgetItem.First()
    
    st = self.FormContainer.Show()
    if st == 1:
      uipBudgetItem = self.uipBudgetItem
      self.Account_Code = uipBudgetItem.BudgetItemCode
      self.Account_Name = uipBudgetItem.BudgetItemDescription
    #-- if

    return st



