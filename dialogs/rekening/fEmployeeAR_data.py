import com.ihsan.foundation.pobjecthelper as phelper
import simplejson

def FormSetDataEx(uideflist, params) :
  config = uideflist.config

  rec = uideflist.uipEmployeeAR.Dataset.AddRecord()
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])

  Now = config.Now()
  
  y = config.ModLibUtils.DecodeDate(Now)[0]
  rec.BeginDate = config.ModLibUtils.EncodeDate(y,1,1)
  rec.EndDate = int(Now)

AUTHSTATUS = {
      'T' : 'Sudah Otorisasi',
      'F' : 'Belum Otorisasi'
      }
def GetHistTransaction(config, params, returns):
  def AsDateTime(tdate):
    utils = config.ModLibUtils
    return utils.EncodeDate(tdate[0], tdate[1], tdate[2])

  helper = phelper.PObjectHelper(config)

  rec = params.FirstRecord
  AccountNo = rec.AccountNo
  BeginDate = int(rec.BeginDate)
  EndDate   = int(rec.EndDate)
  IsAllEmployee = rec.IsAllEmployee
  BranchCode = config.SecurityContext.GetUserInfo()[4]

  # Preparing returns
  AccountReceivable = helper.GetObject('EmployeeAccountReceivable',AccountNo)
  
  BeginningBalance = AccountReceivable.GetBalanceByDate(BeginDate)

  if BeginDate == EndDate :
    PeriodStr = config.FormatDateTime('dd-mm-yyyy',BeginDate)
  else:
    PeriodStr = "%s s/d %s" % (
                   config.FormatDateTime('dd-mm-yyyy',BeginDate),
                   config.FormatDateTime('dd-mm-yyyy',EndDate)
                 )
  # end if

  recSaldo = returns.CreateValues(
          ['BeginningBalance', BeginningBalance or 0.0],
          ['PeriodStr',PeriodStr],
          ['TotalDebet',0.0],
          ['TotalCredit',0.0],
          ['TotalBalance',BeginningBalance or 0.0],
        )

  #--- GET HISTORI TRANSAKSI
  dsHist = returns.AddNewDatasetEx(
    'histori',
    ';'.join([
      'TransactionItemId: integer',
      'TransactionDate: datetime',
      'TransactionDateStr: string',
      'TransactionCode: string',
      'MutationType: string',
      'Amount: float',
      'Debet: float',
      'Kredit: float',
      'ReferenceNo: string',
      'Description: string',
      'Inputer: string',
      'TransactionNo:string',
      'Total:float',
      'AuthStatus:string'
    ])
  )

  AddParam = ''
  if IsAllEmployee == 'F' :
    AddParam += " AccountNo = '%s' and " % AccountNo
    
  s = " \
    SELECT FROM AccountTransactionItem \
    [ \
      %s \
      LTransaction.ActualDate >= :BeginDate and \
      LTransaction.ActualDate < :EndDate and \
      LTransaction.BranchCode = :BranchCode and \
      LTransaction.TransactionCode in {'EAR','PEAR'} \
    ] \
    ( \
      TransactionItemId, \
      LTransaction.TransactionDate, \
      LTransaction.ActualDate, \
      LTransaction.TransactionCode, \
      MutationType, \
      Amount, \
      LTransaction.ReferenceNo, \
      LTransaction.Description, \
      LTransaction.Inputer, \
      LTransaction.TransactionNo,\
      LTransaction.AuthStatus,\
      Self \
    ) \
    THEN ORDER BY ASC ActualDate, ASC TransactionItemId;" % AddParam

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('BeginDate', BeginDate)
  oql.SetParameterValueByName('EndDate', EndDate + 1)
  oql.SetParameterValueByName('BranchCode', BranchCode)
  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  TotalDebet = 0.0
  TotalCredit = 0.0
  while not ds.Eof:
    recHist = dsHist.AddRecord()
    recHist.TransactionItemId = ds.TransactionItemId
    recHist.TransactionDate = AsDateTime(ds.ActualDate)
    recHist.TransactionDateStr = config.FormatDateTime('dd-mmm-yyyy',recHist.TransactionDate)
    recHist.TransactionCode = ds.TransactionCode
    recHist.MutationType = ds.MutationType
    recHist.Amount = ds.Amount
    if ds.MutationType == 'D' :
      recHist.Debet = ds.Amount
      recSaldo.TotalBalance += ds.Amount
      TotalDebet += ds.Amount
    else:
      recHist.Kredit = ds.Amount
      recSaldo.TotalBalance -= ds.Amount
      TotalCredit += ds.Amount
    # endif
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description
    recHist.Inputer = ds.Inputer
    recHist.TransactionNo = ds.TransactionNo
    recHist.AuthStatus = AUTHSTATUS[ds.AuthStatus]

    ds.Next()
  #-- while

  recSaldo.TotalDebet = TotalDebet
  recSaldo.TotalCredit = TotalCredit

