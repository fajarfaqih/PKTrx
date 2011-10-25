import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormOnSetDataEx(uideflist,parameters):
  config = uideflist.config
  param = parameters.FirstRecord
  
  helper = phelper.PObjectHelper(config)

  YearBudgetId = param.BudgetId
  oBudgetYear = helper.GetObject('BudgetYear',YearBudgetId)

  
  rec = uideflist.uipBudget.Dataset.AddRecord()
  rec.BudgetId = oBudgetYear.BudgetId
  rec.BudgetCode = oBudgetYear.BudgetCode
  rec.ItemGroup = oBudgetYear.LBudgetItem.LParent.BudgetItemDescription
  rec.ItemName = oBudgetYear.LBudgetItem.BudgetItemDescription #oBudgetYear.ItemName
  rec.TotalAmount = oBudgetYear.Amount
  rec.OwnerId = oBudgetYear.OwnerId
  rec.PeriodId = oBudgetYear.PeriodId
  
  for i in range(1,13):
    oBudget = helper.GetObjectByNames(
       'Budget',
       {'ParentBudgetId' : YearBudgetId,
         'LPeriod.PeriodValue':i}
    )
    
    rec.SetFieldByName('Amount'+str(i),oBudget.Amount)

def SimpanData(config,parameters,returns):
  status = returns.CreateValues(
      ['Is_Err',0],
      ['Err_Message',''],
      ['BudgetId',0],
  )

  config.BeginTransaction()
  try:
    helper = phelper.PObjectHelper(config)

    param = parameters.FirstRecord
    
    YearBudgetId = param.BudgetId
    YearPeriodId = param.PeriodId
    OwnerId = param.OwnerId
    BranchCode = config.SecurityContext.GetUserInfo()[4]
    
    oBudgetYear = helper.GetObject('BudgetYear',YearBudgetId)
    oBudgetYear.BudgetCode = param.BudgetCode
    
    #oBudgetYear.ItemCode = ''
    #oBudgetYear.ItemName = param.ItemName #rec.BudgetItemDescription
    oBudgetItem = helper.GetObject('BudgetItem',oBudgetYear.ItemId)
    oBudgetItem.BudgetItemDescription = param.ItemName
    oBudgetItem.LParent.BudgetItemDescription = param.ItemGroup

    PeriodList = {}
    TotalAmount = 0.0
    for i in range(1,13) :
      oBudget = helper.GetObjectByNames(
       'Budget',
       {'ParentBudgetId' : YearBudgetId,
         'LPeriod.PeriodValue':i}
      )
      oBudget.BudgetCode = param.BudgetCode
      oBudget.ItemCode = ''
      oBudget.ItemName = param.ItemName #rec.BudgetItemDescription
      oBudget.Amount = param.GetFieldByName('Amount' + str(i)) or 0.0

      TotalAmount += oBudget.Amount

    oBudgetYear.Amount = TotalAmount

    config.Commit()
    status.BudgetId = oBudgetYear.BudgetId
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
