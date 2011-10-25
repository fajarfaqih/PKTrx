class fSelectBudgetOwner :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.OwnerId = None
    self.OwnerName = None

  def GetOwner(self,ItemCode,PeriodId):
    uipBudgetOwner = self.uipBudgetOwner
      
    ph = self.app.CreateValues(['ItemCode', ItemCode], ['PeriodId', PeriodId])
    self.FormObject.SetDataWithParameters(ph)
    self.uipBudgetOwner.First()
    
    st = self.FormContainer.Show()
    if st == 1:
      uipBudgetOwner = self.uipBudgetOwner
      self.OwnerId = uipBudgetOwner.OwnerId
      self.OwnerName = uipBudgetOwner.OwnerName
    #-- if

    return st



