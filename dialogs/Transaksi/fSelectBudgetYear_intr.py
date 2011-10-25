class fSelectBudgetYear :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.ProductId = None
    self.ProductName = None
    self.FundCategory = None
    self.PercentageOfAmilFunds = 0.0
    self.BudgetId = 0
    self.BudgetCode = ''
    self.OwnerName = ''
    self.ItemGroup = ''
    self.ItemDetail = ''
    
  def OnDoubleClick(self,sender):
    self.FormObject.Close(1)
    
  def GetBudgetCode(self, BranchCode,PeriodId):
    self.qBudget.OQLText = "\
        SELECT FROM BudgetYear \
        [ \
          BranchCode = :BranchCode and \
          PeriodId = :PeriodId \
        ] \
        ( \
          BudgetId, \
          ItemCode, \
          ItemName, \
          BudgetCode, \
          Amount, \
          Realization, \
          CurrencyCode, \
          RevisionID, \
          PeriodId, \
          LOwner.OwnerName, \
          LBudgetItem.LParent.ItemId, \
          LBudgetItem.LParent.BudgetItemDescription as ItemGroup, \
          LBudgetItem.BudgetItemDescription as ItemDetail, \
          Self \
        ) \
        THEN ORDER BY ASC BudgetCode;"
    self.qBudget.SetParameter('BranchCode', BranchCode)
    self.qBudget.SetParameter('PeriodId', PeriodId)
    
    self.qBudget.DisplayData()
    
    st = self.FormContainer.Show()
    if st == 1:
      self.BudgetId = self.qBudget.GetFieldValue('BudgetYear.BudgetId')
      self.BudgetCode = self.qBudget.GetFieldValue('BudgetYear.BudgetCode')
      self.OwnerName = self.qBudget.GetFieldValue('BudgetYear.OwnerName')
      self.ItemGroup = self.qBudget.GetFieldValue('BudgetYear.ItemGroup')
      self.ItemDetail = self.qBudget.GetFieldValue('BudgetYear.ItemDetail')


    return st

