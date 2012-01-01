class fSelectBudgetCode :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.ItemCode = None
    self.ItemName = None

  def GetBudget(self, ActualDate):

    uipFilter = self.uipFilter
    uipFilter.Edit()
    #uipFilter.PeriodId = PeriodId
    uipFilter.ActualDate = ActualDate

    if uipFilter.FilterCategory in [None,''] :
      uipFilter.FilterCategory = '0'
      uipFilter.FilterText = ''
    
    self.ShowData()
    
    uipBudget = self.uipBudget
    self.uipBudget.First()
    
    st = self.FormContainer.Show()
    if st == 1:
      uipBudget = self.uipBudget
      self.BudgetCode = uipBudget.BudgetCode
      self.BudgetOwner = uipBudget.BudgetOwner
      self.BudgetId = uipBudget.BudgetId
    #-- if

    return st

  def ShowData(self):
    uipFilter = self.uipFilter

    ph = self.app.CreateValues(
      ['ActualDate', uipFilter.ActualDate],
      ['FilterCategory', uipFilter.FilterCategory or ''],
      ['FilterText', uipFilter.FilterText or '']
    )
    self.uipBudget.ClearData()
    self.FormObject.SetDataWithParameters(ph)
    
  def FilterCategoryChange(self,sender):
    if sender.ItemIndex == 0 :
      uipFilter = self.uipFilter
      uipFilter.FilterText = ''
    self.pFilter_FilterText.enabled = (sender.ItemIndex != 0)

  def ApplyFilterClick(self,sender):
    self.ShowData()
    
  def GridDoubleClick(self,sender):
    self.SelectClick(self.pSelect_bSelect)
    
  def SelectClick(self,sender):
    self.FormObject.Close(1)
