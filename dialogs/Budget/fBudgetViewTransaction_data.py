import com.ihsan.foundation.pobjecthelper as phelper
import simplejson

def FormSetDataEx(uideflist, parameters) :
  config = uideflist.config

  if parameters.DatasetCount == 0 : return 1


  param = parameters.FirstRecord

  helper = phelper.PObjectHelper(config)

  YearBudgetId = param.BudgetId
  oBudgetYear = helper.GetObject('BudgetYear',YearBudgetId)

  rec = uideflist.uipBudget.Dataset.AddRecord()
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.BeginDate = int(config.Now())
  rec.EndDate = rec.BeginDate
  rec.OwnerName = oBudgetYear.LOwner.OwnerName
  rec.Tahun = oBudgetYear.LPeriod.PeriodValue
  rec.BudgetCode = oBudgetYear.BudgetCode
  rec.ItemGroup = oBudgetYear.LBudgetItem.LParent.BudgetItemDescription #oBudgetYear.ItemName
  rec.ItemName = oBudgetYear.LBudgetItem.BudgetItemDescription #oBudgetYear.ItemName
  rec.BudgetId = YearBudgetId
  

def GetHistTransaction(config, params, returns):
  def AsDateTime(tdate):
    utils = config.ModLibUtils
    return utils.EncodeDate(tdate[0], tdate[1], tdate[2])

  helper = phelper.PObjectHelper(config)

  rec = params.FirstRecord
  BudgetId = rec.BudgetId
  BeginDate = rec.BeginDate
  EndDate   = rec.EndDate

  if BeginDate == EndDate:
     Tanggal = '%s' % config.FormatDateTime('dd/mm/yyyy', BeginDate)
  else:
     Tanggal = '%s - %s' % (
                 config.FormatDateTime('dd/mm/yyyy', BeginDate),
                 config.FormatDateTime('dd/mm/yyyy', EndDate)
               )
               
  # Preparing returns
  status = returns.CreateValues(
     ['Tanggal',Tanggal],
     ['TotalAmount', 0.0],
  )
  dsHist = returns.AddNewDatasetEx(
    'histori',
    ';'.join([
      'TransactionItemId: integer',
      'TransactionDate: datetime',
      'TransactionDateStr: string',
      'TransactionCode: string',
      'TransactionType: string',
      'MutationType: string',
      'Amount: float',
      'AmountEkuivalen: float',
      'Rate: float',
      'CurrencyCode: string',
      'CurrencyName: string',
      'ReferenceNo: string',
      'Description: string',
      'Inputer: string',
      'NoTransaksi:string',
      'OwnerName:string',
      'OwnerCode:string',
      'BudgetCode:string',
      'GroupName:string',
      'ItemName:string',
      'BudgetTransTypeDesc:string'
    ])
  )


  s = ' \
    SELECT FROM BudgetTransaction \
    [ \
      BudgetId = :BudgetId and \
      LTransaction.LTransaction.ActualDate >= :BeginDate \
      and LTransaction.LTransaction.ActualDate < :EndDate \
    ] \
    ( \
      LTransaction.TransactionItemId, \
      LTransaction.LTransaction.ActualDate, \
      LTransaction.LTransaction.TransactionCode, \
      LTransaction.LTransaction.LTransactionType.Description as TransactionType, \
      LTransaction.MutationType, \
      LTransaction.Amount, \
      LTransaction.Ekuivalenamount, \
      LTransaction.Rate, \
      LTransaction.CurrencyCode, \
      LTransaction.LCurrency.Short_Name, \
      LTransaction.LTransaction.Rate as TransRate, \
      LTransaction.LTransaction.CurrencyCode as TransCurrencyCode, \
      LTransaction.LTransaction.LCurrency.Short_Name as TransCurrencyName, \
      LTransaction.LTransaction.ReferenceNo, \
      LTransaction.LTransaction.Description, \
      LTransaction.LTransaction.Inputer, \
      LTransaction.LTransaction.TransactionNo,\
      LBudget.BudgetCode, \
      LBudget.LBudgetItem.LParent.BudgetItemDescription as ItemGroup, \
      LBudget.LBudgetItem.BudgetItemDescription as ItemDetail, \
      LBudget.LOwner.OwnerName, \
      LBudget.LOwner.OwnerCode, \
      self.BudgetTransType, \
      self.BudgetTransType $ as BudgetTransTypeDesc,  \
      Self \
    ) \
    THEN ORDER BY ASC ActualDate, ASC TransactionItemId;'

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('BudgetId', BudgetId)
  oql.SetParameterValueByName('BeginDate', int(BeginDate))
  oql.SetParameterValueByName('EndDate', int(EndDate) + 1)

  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  TotalAmount = 0.0
  while not ds.Eof:
    recHist = dsHist.AddRecord()
    recHist.TransactionItemId = ds.TransactionItemId
    recHist.TransactionDate = AsDateTime(ds.ActualDate)
    recHist.TransactionDateStr = config.FormatDateTime('dd-mmm-yyyy',recHist.TransactionDate)
    recHist.TransactionCode = ds.TransactionCode
    recHist.TransactionType = ds.Description
    recHist.MutationType = ds.MutationType

    TranCurrencyCode = ds.CurrencyCode_1
    TranCurrencyName = ds.Short_Name_1
    TransRate        = ds.Rate_1

    if ds.CurrencyCode != TranCurrencyCode and ds.CurrencyCode == '000':
      CurrencyCode = TranCurrencyCode
      CurrencyName = TranCurrencyName
      Rate = TransRate
      Amount      = ds.Amount / Rate
    else :
      CurrencyCode = ds.CurrencyCode
      CurrencyName = ds.Short_Name
      Rate = ds.Rate
      Amount = ds.Amount
    # end if

    recHist.Amount = Amount
    recHist.Rate = Rate
    recHist.AmountEkuivalen = ds.Ekuivalenamount
    
    if ds.BudgetTransType == 'R' :
      recHist.Amount = -1 * Amount
      recHist.AmountEkuivalen = -1 * ds.Ekuivalenamount
    # end if

    TotalAmount += ds.Ekuivalenamount
    
    recHist.CurrencyCode = CurrencyCode
    recHist.CurrencyName = CurrencyName
    
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description_1
    recHist.Inputer = ds.Inputer
    recHist.NoTransaksi = ds.TransactionNo
    recHist.BudgetTransTypeDesc = ds.Enum_Description

    ds.Next()
  #-- while
  status.TotalAmount = TotalAmount
