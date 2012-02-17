import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormSetDataEx(uideflist,params):
  config = uideflist.config
  
  helper = phelper.PObjectHelper(config)

  sPeriod = 'select * from budgetperiod where parentperiod is null'
  
  rsPeriod = config.CreateSQL(sCheck).RawResult
  
  while not rsPeriod.Eof:
    pass

def GetRefData(config,params,returns):

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
  
def ExecuteImport(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
  )
  
  config.BeginTransaction()
  try:
    app = config.AppObject
    app.ConCreate('BUDGET')
    app.ConWriteln('Proses Uploda Data Budget','BUDGET')
    
    helper = phelper.PObjectHelper(config)

    uipBudgetDetail = params.uipBudgetDetail
    
    YearPeriodId = params.uipData.GetRecord(0).Tahun
    BranchCode = config.SecurityContext.GetUserInfo()[4]
    
    totaldata = uipBudgetDetail.RecordCount
    OwnerList = {}
    PeriodList = {}
    message = ''
    PrevItemGroup = ''

    app.ConWriteln('Total Data %d ' % totaldata ,'BUDGET')
    for rowdata in range(totaldata):
      app.ConWriteln('Proses data ke-%d dari %d ' % (rowdata + 1, totaldata) ,'BUDGET')
      recBudget = uipBudgetDetail.GetRecord(rowdata)
      if OwnerList.has_key(recBudget.OwnerCode) :
        OwnerId = OwnerList[recBudget.OwnerCode]
      else:
        oOwner = helper.GetObjectByNames('BudgetOwner',{'OwnerCode' : recBudget.OwnerCode})
        if oOwner.isnull : raise 'PERINGATAN','Kode Pemilik Anggaran Tidak Terdaftar'
        OwnerId = oOwner.OwnerID
        OwnerList[recBudget.OwnerCode] = oOwner.OwnerID

      oBudgetYear = helper.CreatePObject('BudgetYear')
      oBudgetYear.PeriodID = YearPeriodId
      oBudgetYear.OwnerID = OwnerId
      oBudgetYear.BudgetCode = recBudget.BudgetCode
      
      ItemGroup = recBudget.ItemGroup
      if ItemGroup != PrevItemGroup :
        oItemGroup = helper.CreatePObject('BudgetItem')
        oItemGroup.Is_Detail = 'F'
        oItemGroup.BudgetItemDescription = ItemGroup
        oItemGroup.BudgetItemName = ItemGroup
        oItemGroup.Level = 1
        oItemGroup.OwnerId = OwnerId
        oItemGroup.SetHierarchy()
        oItemGroup.BranchCode = BranchCode
        GroupItemId = oItemGroup.ItemId
        
        PrevItemGroup = ItemGroup
        
      ItemName = recBudget.ItemName
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
      oBudgetYear.ItemId = ItemId
      oBudgetYear.ItemCode = ''
      oBudgetYear.ItemName = '' #rec.BudgetItemDescription
      oBudgetYear.CurrencyCode = '000'
      oBudgetYear.Realization = 0.0
      oBudgetYear.BranchCode = BranchCode
      oBudgetYear.IsDetail = 'F'

      TotalAmount = 0.0
      for i in range(1,13) :
        if PeriodList.has_key(i) :
          PeriodId = PeriodList[i]
        else:
          #OwnerId = recBudget.OwnerCode
          oPeriod = helper.GetObjectByNames('BudgetPeriod',
              { 'ParentPeriodId' : YearPeriodId,
                'PeriodValue' : i
              }
          )
          PeriodId = oPeriod.PeriodID
          PeriodList[i] = oPeriod.PeriodID

        oBudget = helper.GetObjectByNames('Budget',
            {'PeriodId':PeriodId,
             'OwnerId' :OwnerId,
             'BranchCode' : BranchCode,
             'BudgetCode' : recBudget.BudgetCode,
             'CurrencyCode' : '000',
            }
        )
        if not oBudget.isnull :
          message += ' nomor %s \n' % str(recBudget.RowNumber)
          break

        oBudget = helper.CreatePObject('Budget')
        oBudget.ItemId = ItemId
        oBudget.PeriodID = PeriodId
        oBudget.OwnerID = OwnerId
        oBudget.BudgetCode = recBudget.BudgetCode
        oBudget.ItemCode = ''
        oBudget.ItemName = '' #rec.BudgetItemDescription
        oBudget.CurrencyCode = '000'
        oBudget.Amount = recBudget.GetFieldByName('amount' + str(i)) or 0.0
        oBudget.Realization = 0.0
        oBudget.BranchCode = BranchCode
        oBudget.IsDetail = 'T'
        oBudget.ParentBudgetId = oBudgetYear.BudgetId
        TotalAmount += oBudget.Amount

      oBudgetYear.Amount = TotalAmount
      
    if message != '' :
      message = 'Berdasarkan Kode Anggaran. Data pada file dengan nomor di bawah ini terjadi duplikasi kode anggaran \n' + message
      raise '',message
      
    config.Commit()
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
    

"""
    OwnerId = recBudget.GetFieldByName('LBudgetOwner.OwnerID')
    PeriodId = recBudget.PeriodID

    dsBudgetItem = parameters.uipBudgetItem
    TotalBudgetItem = dsBudgetItem.RecordCount

    i = 0

    while i < TotalBudgetItem :
      rec = dsBudgetItem.GetRecord(i)
      AccountCode = rec.BudgetItemCode

      sCheck = "select count(budgetid) \
                 from budget \
                 where ownerid=%d \
                   and itemcode='%s' \
                   and periodid=%d " % (OwnerId,AccountCode,PeriodId)

      rsCheck = config.CreateSQL(sCheck).RawResult
      if rsCheck.GetFieldValueAt(0) > 0 :
         raise '','Item anggaran dengan account code %s telah ada dalam periode yang diinput' % AccountCode
      oBudget = helper.CreatePObject('Budget')
      oBudget.PeriodID = PeriodId
      oBudget.OwnerID = OwnerId
      oBudget.ItemCode = AccountCode
      oBudget.ItemName = rec.BudgetItemDescription
      oBudget.CurrencyCode = rec.GetFieldByName('LValuta.Currency_Code')
      oBudget.Amount = rec.Amount
      oBudget.Realization = 0.0
      i += 1
    # end while"""
