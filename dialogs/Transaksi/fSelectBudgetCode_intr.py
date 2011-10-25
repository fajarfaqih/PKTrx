class fSelectBudgetCode :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.ItemCode = None
    self.ItemName = None

  def GetBudget(self,PeriodId):
    uipBudget = self.uipBudget
      
    ph = self.app.CreateValues(['PeriodId', PeriodId])
    self.FormObject.SetDataWithParameters(ph)
    self.uipBudget.First()
    
    st = self.FormContainer.Show()
    if st == 1:
      uipBudget = self.uipBudget
      self.BudgetCode = uipBudget.BudgetCode
      self.BudgetOwner = uipBudget.BudgetOwner
      self.BudgetId = uipBudget.BudgetId
    #-- if

    return st

