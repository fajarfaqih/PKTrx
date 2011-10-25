import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormSetDataEx(uideflist, parameters) :

  if parameters.DatasetCount == 0 : return 1
  
  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  param = parameters.FirstRecord
  
  PeriodId= param.PeriodId
  OwnerId= param.OwnerId
  
  sBudget = 'select * from budget \
             where ownerid=%d and periodid=%d' % (
             OwnerId,PeriodId)
             
  rsBudget = config.CreateSQL(sBudget).RawResult
  rsBudget.First()
  while not rsBudget.Eof:
    rec = uideflist.uipBudgetItem.Dataset.AddRecord()
    rec.AccountCode = rsBudget.ItemCode
    rec.AccountName = rsBudget.ItemName
    rec.CurrencyCode = rsBudget.CurrencyCode
    if rsBudget.RevisionID not in [None,0]:
      oRevision = helper.GetObject('BudgetRevision',rsBudget.RevisionID)
      rec.Amount = oRevision.Amount
    else:
      rec.Amount = rsBudget.Amount
    rec.OriAmount = rec.Amount
    rec.Realization = rsBudget.Realization
    rec.BudgetId = rsBudget.BudgetId
    rsBudget.Next()

def SimpanData(config,parameters,returns):

  status = returns.CreateValues(
      ['Is_Err',0],
      ['Err_Message','']
  )
  
  config.BeginTransaction()
  try:
    helper = phelper.PObjectHelper(config)
    
    # Get Info Owner & Period
    recBudget = parameters.uipBudget.GetRecord(0)
    
    #OwnerId = recBudget.GetFieldByName('LBudgetOwner.OwnerID')
    #PeriodId = recBudget.PeriodID
    
    dsBudgetItem = parameters.uipBudgetItem
    TotalBudgetItem = dsBudgetItem.RecordCount
    
    i = 0
    while i < TotalBudgetItem :
      rec = dsBudgetItem.GetRecord(i)
      if rec.Amount <> rec.OriAmount :
        oBudget = helper.GetObject('Budget',rec.BudgetId)
        oBudget.CreateRevision(rec.Amount)

      #AccountCode = rec.GetFieldByName('LAccount.Account_Code')
      
      #sCheck = "select count(budgetid) \
      #           from budget \
      #           where ownerid=%d \
      #             and itemcode='%s' \
      #             and periodid=%d " % (OwnerId,AccountCode,PeriodId)
                   
      #rsCheck = config.CreateSQL(sCheck).RawResult
      #if rsCheck.GetFieldValueAt(0) > 0 :
      #   raise '','Item anggaran dengan account code %s telah ada dalam periode yang diinput' % AccountCode
      #oBudget = helper.CreatePObject('Budget')
      #oBudget.PeriodID = PeriodId
      #oBudget.OwnerID = OwnerId
      #oBudget.ItemCode = AccountCode
      #oBudget.ItemName = rec.GetFieldByName('LAccount.Account_Name')
      #oBudget.CurrencyCode = rec.GetFieldByName('LValuta.Currency_Code')
      #oBudget.Amount = rec.Amount
      #oBudget.Realization = rec.Realization
      i += 1
    # end while
    
    config.Commit()
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
