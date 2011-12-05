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
      'ReferenceNo: string',
      'Description: string',
      'Inputer: string',
      'NoTransaksi:string',
      'BudgetTransactionType:string'
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
      LTransaction.LTransaction.ReferenceNo, \
      LTransaction.LTransaction.Description, \
      LTransaction.LTransaction.Inputer, \
      LTransaction.LTransaction.TransactionNo,\
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
    recHist.Amount = ds.Amount
    TotalAmount += ds.Amount
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description_1
    recHist.Inputer = ds.Inputer
    recHist.NoTransaksi = ds.TransactionNo
    recHist.BudgetTransactionType = ds.Enum_Description

    ds.Next()
  #-- while
  status.TotalAmount = TotalAmount
