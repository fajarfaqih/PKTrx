import com.ihsan.foundation.pobjecthelper as phelper
import simplejson


def SearchCashAccount(config, params, returns):
  helper = phelper.PObjectHelper(config)
  oAccount = helper.GetObject('CashAccount',
    params.FirstRecord.AccountNo).CastToLowestDescendant()
  
  retparam = []
  retparam.append(['BranchCode', oAccount.BranchCode])
  retparam.append(['CurrencyCode', oAccount.CurrencyCode])
  retparam.append(['Balance', oAccount.Balance])

  if oAccount.IsA('BankCash'):
    retparam.append(['BankAccountNo', oAccount.BankAccountNo])
    retparam.append(['BankName', oAccount.BankName])
  elif oAccount.IsA('PettyCash'):
    retparam.append(['UserName', oAccount.Username])

  eval('returns.CreateValues'+str(tuple(retparam)))

def GetHistTransaction(config, params, returns):
  def AsDateTime(tdate):
    utils = config.ModLibUtils
    return utils.EncodeDate(tdate[0], tdate[1], tdate[2])

  helper = phelper.PObjectHelper(config)

  rec = params.FirstRecord
  AccountNo = rec.AccountNo
  BeginDate = rec.BeginDate
  EndDate   = rec.EndDate

  # Preparing returns
  recSaldo = returns.CreateValues(['BeginningBalance', 0.0])
  dsHist = returns.AddNewDatasetEx(
    'histori',
    ';'.join([
      'TransactionItemId: integer',
      'TransactionDate: datetime',
      'TransactionCode: string',
      'TransactionNo: string',
      'MutationType: string',
      'Amount: float',
      'ReferenceNo: string',
      'Description: string',
      'Inputer: string'
    ])
  )

  s = ' \
    SELECT FROM AccountTransactionItem \
    [ \
      AccountNo = :AccountNo and \
      LTransaction.TransactionDate >= :BeginDate and \
      LTransaction.TransactionDate < :EndDate \
    ] \
    ( \
      TransactionItemId, \
      LTransaction.TransactionDate, \
      LTransaction.TransactionCode, \
      MutationType, \
      Amount, \
      LTransaction.ReferenceNo, \
      LTransaction.Description, \
      LTransaction.TransactionNo, \
      LTransaction.Inputer, \
      Self \
    ) \
    THEN ORDER BY ASC TransactionDate, ASC TransactionItemId;'

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('AccountNo', AccountNo)
  oql.SetParameterValueByName('BeginDate', BeginDate)
  oql.SetParameterValueByName('EndDate', EndDate + 1)
  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  while not ds.Eof:
    recHist = dsHist.AddRecord()
    recHist.TransactionItemId = ds.TransactionItemId
    recHist.TransactionDate = AsDateTime(ds.TransactionDate)
    recHist.TransactionCode = ds.TransactionCode
    recHist.MutationType = ds.MutationType
    recHist.Amount = ds.Amount
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description
    recHist.Inputer = ds.Inputer
    recHist.TransactionNo = ds.TransactionNo

    ds.Next()
  #-- while
  
