class fBudgetViewDetail:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.BudgetId = 0

  def FormOnShow(self,sender):
    self.pBudget_BudgetCode.SetFocus()
    #self.form.SetAllControlsReadOnly()
    
  def ViewData(self,BudgetId):
    self.uipBudget.ClearData()

    ph = self.app.CreateValues(
               ['BudgetId', BudgetId],
    )
    self.form.SetDataWithParameters(ph)

    if self.FormContainer.Show() == 1:
      return 1
    else:
      return 0
    
    
    
