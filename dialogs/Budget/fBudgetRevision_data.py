import com.ihsan.foundation.pobjecthelper as phelper
import sys
import simplejson


def FormSetDataEx(uideflist, params) :
  config = uideflist.config
  helper = phelper.PObjectHelper(uideflist.config)

  BudgetId = params.FirstRecord.BudgetId
  
  oBudget = helper.GetObject( 'Budget',BudgetId)

  rec = uideflist.uipBudget.Dataset.AddRecord()

  rec.BudgetId = BudgetId
  rec.OwnerName = oBudget.LOwner.OwnerName
  rec.Bulan = oBudget.LPeriod.PeriodValue
  rec.Tahun = oBudget.LPeriod.LParent.PeriodValue
  
  #sRevision = 'select * from BudgetRevision where budgetid=%d order by revisionid' % BudgetId
  #rsRevision = config.CreateSQL(sRevision).RawResult

  #if rsRevision.eof:
  if oBudget.RevisionId in [None,0]:
    rec.Amount = oBudget.Amount
  else:
    rec.Amount = oBudget.LLastRevision.Amount
  # endif
  
def SaveRevision(config, params, returns):
  helper = phelper.PObjectHelper(config)
  status = returns.CreateValues(['IsErr', 0], ['ErrMessage', ''])
  config.BeginTransaction()
  try :
    param = params.FirstRecord
    BudgetId = param.BudgetId
    Amount = param.Amount

    oBudget = helper.GetObject('Budget',BudgetId)
    oBudget.CreateRevision(Amount)
    
    config.Commit()
  except :
    config.Rollback()
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])


