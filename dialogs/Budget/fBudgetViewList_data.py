import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormSetDataEx(uideflist, parameters) :
  config = uideflist.Config

  if parameters.DatasetCount == 0 :
    rec = uideflist.uipBudget.Dataset.AddRecord()

    BranchCode = config.SecurityContext.GetUserInfo()[4]
    BranchName = config.SecurityContext.GetUserInfo()[5]
    rec.BranchCode = BranchCode
    rec.BranchName = BranchName
    rec.HeadOfficeCode = config.SysVarIntf.GetStringSysVar('OPTION','HeadOfficeCode')

    return 1
  
  helper = phelper.PObjectHelper(config)
  param = parameters.FirstRecord
  
  PeriodId= param.PeriodId
  OwnerId= param.OwnerId
  IsAllOwner = param.IsAllOwner
  BranchCode = param.BranchCode

  ds  = RunOQLDataBudget(config,OwnerId,PeriodId,BranchCode,IsAllOwner)

  while not ds.Eof:
#  sBudget = 'select * from budget \
#             where ownerid=%d and periodid=%d' % (
#             OwnerId,PeriodId)
             
#  rsBudget = config.CreateSQL(sBudget).RawResult
#  rsBudget.First()
#  while not rsBudget.Eof:

    rec = uideflist.uipBudgetItem.Dataset.AddRecord()
    rec.BudgetCode = ds.BudgetCode
    rec.Amount = ds.Amount or 0.0
    #rec.ItemName = ds.ItemName
    rec.BudgetId = ds.BudgetId
    rec.Realization = ds.Realization or 0.0
    rec.ItemGroup = ds.BudgetItemDescription
    rec.ItemName = ds.BudgetItemDescription_1
    rec.SalvageValue = rec.Amount - rec.Realization
    rec.OwnerName = ds.OwnerName

    #Amount = ds.Amount or 0.0
    #for i in range(11):
      #Amount +=ds.Amount or 0.0
      #ds.Next()
    #rec.Amount = Amount
    #rec.AccountCode = rsBudget.ItemCode
    #rec.AccountName = rsBudget.ItemName
    #rec.CurrencyCode = rsBudget.CurrencyCode
    #if rsBudget.RevisionID not in [None,0]:
    #  oRevision = helper.GetObject('BudgetRevision',rsBudget.RevisionID)
    #  rec.Amount = oRevision.Amount
    #else:
    #  rec.Amount = rsBudget.Amount
    #rec.OriAmount = rec.Amount
    #rec.Realization = rsBudget.Realization
    #rec.BudgetId = rsBudget.BudgetId
    #rsBudget.Next()
    ds.Next()

def RunOQLDataBudget(config,OwnerId,PeriodId,BranchCode,IsAllOwner):
  AddParam = ''
  if IsAllOwner == 'F' :
    AddParam = " and OwnerId = %d " % OwnerId
    
  s = ' \
    SELECT FROM BudgetYear \
    [ \
      PeriodId = :PeriodId and \
      BranchCode = :BranchCode \
      %s \
    ] \
    ( \
      ItemCode, \
      ItemName, \
      BudgetCode, \
      Amount, \
      Realization, \
      CurrencyCode, \
      RevisionID, \
      PeriodId, \
      LBudgetItem.LParent.ItemId, \
      LBudgetItem.LParent.BudgetItemDescription as ItemGroup, \
      LBudgetItem.BudgetItemDescription as ItemDetail, \
      LOwner.OwnerName, \
      Self \
    ) \
    THEN ORDER BY ASC ItemId, ASC BudgetCode, ASC PeriodId;' % AddParam


  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('PeriodId', PeriodId)
  oql.SetParameterValueByName('BranchCode', BranchCode)

  oql.ApplyParamValues()

  oql.active = 1
  return oql.rawresult

def GetBudgetData(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['BranchName',''],
    ['OwnerName',''],
    ['PeriodYear',0],
  )

  try:
    helper = phelper.PObjectHelper(config)
    param = params.FirstRecord
    OwnerId = param.OwnerId
    PeriodId = param.PeriodId
    BranchCode = param.BranchCode
    IsAllOwner = param.IsAllOwner
    
    dsBudgetData = returns.AddNewDatasetEx(
          'budgetdata',
          ';'.join(
          ['BudgetCode : string' ,
           'Amount : float',
           'BudgetId : integer',
           'Realization : float',
           'ItemGroup : string',
           'ItemName : string',
           'SalvageValue : float',
           'OwnerName : string',
          ])
      )

    oBudgetPeriod = helper.GetObject('BudgetPeriod',PeriodId)
    status.PeriodYear = oBudgetPeriod.PeriodValue
    status.BranchName = config.SecurityContext.GetUserInfo()[5]
    
    ds = RunOQLDataBudget(config,OwnerId,PeriodId,BranchCode,IsAllOwner)
    while not ds.Eof :
      recBudget = dsBudgetData.AddRecord()
      recBudget.BudgetCode = ds.BudgetCode
      recBudget.Amount = ds.Amount or 0.0
      recBudget.BudgetId = ds.BudgetId
      recBudget.Realization = ds.Realization or 0.0
      recBudget.ItemGroup = ds.BudgetItemDescription
      recBudget.ItemName = ds.BudgetItemDescription_1
      recBudget.SalvageValue = recBudget.Amount - recBudget.Realization
      recBudget.OwnerName = ds.OwnerName

      ds.Next()
    # end while

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
  
def GetPeriodYear(config,params,returns):

  ds = returns.AddNewDatasetEx(
        'perioddata',
        ';'.join(
        ['periodid:integer' ,
         'periodvalue:integer'
        ])
    )


  sPeriod = 'select * from budgetperiod where parentperiodid is null'

  rsPeriod = config.CreateSQL(sPeriod).RawResult

  while not rsPeriod.Eof:
    recPeriod = ds.AddRecord()
    recPeriod.periodid = rsPeriod.PeriodId
    recPeriod.periodvalue = rsPeriod.PeriodValue
    rsPeriod.Next()



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
    

def DeleteBudget(config,parameters,returns):

  status = returns.CreateValues(
      ['Is_Err',0],
      ['Err_Message','']
  )

  config.BeginTransaction()
  try:
    helper = phelper.PObjectHelper(config)

    param = parameters.FirstRecord

    #oBudgetYear = helper.GetObject('BudgetYear',param.BudgetId)
    #oBudgetYear.Delete()
    sDelete = 'delete from budget where parentbudgetid=%d' % (param.BudgetId)
    config.ExecSQL(sDelete)
    sDelete = 'delete from budget where budgetid=%d' % (param.BudgetId)
    config.ExecSQL(sDelete)
    
    config.Commit()
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])


