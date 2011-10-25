import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormSetDataEx(uideflist,params):
  config = uideflist.config
  
  if params.DatasetCount == 0 : return 1
  
  recParam = params.FirstRecord
  
  recBudget = uideflist.uipBudget.Dataset.AddRecord()
  recBudget.BranchCode = config.SecurityContext.GetUserInfo()[4]
  recBudget.OwnerId = recParam.OwnerId
  recBudget.PeriodId = recParam.PeriodId

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
    
    YearPeriodId = param.PeriodId
    OwnerId = param.OwnerId
    BranchCode = config.SecurityContext.GetUserInfo()[4]
    ItemName = param.ItemName
    BudgetCode = param.BudgetCode
    NewGroupName = param.NewGroupName or ''
    
    if param.InputGroupType == 'N':
      oItemGroup = helper.CreatePObject('BudgetItem')
      oItemGroup.Is_Detail = 'F'
      oItemGroup.BudgetItemDescription = NewGroupName
      oItemGroup.BudgetItemName = NewGroupName
      oItemGroup.Level = 1
      oItemGroup.OwnerId = OwnerId
      oItemGroup.SetHierarchy()
      GroupItemId = oItemGroup.ItemId
    else:
      GroupItemId = param.GetFieldByName('LGroupItem.ItemId')

    oItemDetail = helper.CreatePObject('BudgetItem')
    oItemDetail.Is_Detail = 'T'
    oItemDetail.BudgetItemDescription = ItemName
    oItemDetail.BudgetItemName = ItemName
    oItemDetail.Level = 2
    oItemDetail.ParentItemId = GroupItemId
    oItemDetail.OwnerId = OwnerId
    oItemDetail.BranchCode = BranchCode
    oItemDetail.SetHierarchy()
    ItemId = oItemDetail.ItemId

    oCheckBudgetYear = helper.GetObjectByNames('BudgetYear',
         {'BudgetCode' : BudgetCode,
          'BranchCode' : BranchCode,
          'PeriodId'   : YearPeriodId,
          'CurrencyCode' : '000',
         }
    )
    if not oCheckBudgetYear.isnull : raise '','Kode Budget yang diinputkan sudah digunakan.\nSilahkan ubah kode budget'
    oBudgetYear = helper.CreatePObject('BudgetYear')
    oBudgetYear.PeriodID = YearPeriodId
    oBudgetYear.OwnerID = OwnerId
    oBudgetYear.BudgetCode = BudgetCode
    oBudgetYear.ItemId = ItemId
    oBudgetYear.ItemCode = ''
    oBudgetYear.ItemName = ItemName #rec.BudgetItemDescription
    oBudgetYear.CurrencyCode = '000'
    oBudgetYear.Realization = 0.0
    oBudgetYear.BranchCode = BranchCode
    oBudgetYear.IsDetail = 'F'

    PeriodList = {}
    TotalAmount = 0.0
    for i in range(1,13) :
      if PeriodList.has_key(i) :
        PeriodId = PeriodList[i]
      else:
        oPeriod = helper.GetObjectByNames('BudgetPeriod',
            { 'ParentPeriodId' : YearPeriodId,
              'PeriodValue' : i
            }
        )
        PeriodId = oPeriod.PeriodID
        PeriodList[i] = oPeriod.PeriodID

      oCheckBudget = helper.GetObjectByNames('Budget',
          {'PeriodId':PeriodId,
           'OwnerId' :OwnerId,
           'BranchCode' : BranchCode,
           'BudgetCode' : param.BudgetCode,
           'CurrencyCode' : '000',
          }
      )
      if not oCheckBudget.isnull :
        message += ' nomor %s \n' % str(recBudget.RowNumber)
        break

      oBudget = helper.CreatePObject('Budget')
      oBudget.ItemId = ItemId
      oBudget.PeriodID = PeriodId
      oBudget.OwnerID = OwnerId
      oBudget.BudgetCode = BudgetCode
      oBudget.ItemCode = ''
      oBudget.ItemName = ItemName #rec.BudgetItemDescription
      oBudget.CurrencyCode = '000'
      oBudget.Amount = param.GetFieldByName('Amount' + str(i)) or 0.0
      oBudget.Realization = 0.0
      oBudget.BranchCode = BranchCode
      oBudget.IsDetail = 'T'
      oBudget.ParentBudgetId = oBudgetYear.BudgetId
      #oBudget.BudgetId = 1

      TotalAmount += oBudget.Amount

    oBudgetYear.Amount = TotalAmount

    config.Commit()
    status.BudgetId = oBudgetYear.BudgetId
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
    
