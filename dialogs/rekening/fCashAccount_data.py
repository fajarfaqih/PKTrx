import com.ihsan.foundation.pobjecthelper as phelper
import simplejson
import sys,os

AUTHSTATUS = {'T' : 'Sudah Otorisasi','F':'Belum Otorisasi'}
def FormSetDataEx(uideflist, parameter) :
    config = uideflist.config
    rec = uideflist.uipCashAccount.Dataset.AddRecord()

    rec.BeginDate = (config.Now())
    rec.EndDate = rec.BeginDate
    rec.BranchCode = config.SecurityContext.GetUserInfo()[4]

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
  recSaldo = returns.CreateValues(
     ['CashAccountNo',''],
     ['CashAccountName',''],
     ['CashAccountBranch',''],
     ['CashAccountCurrency',''],
     ['BeginningBalance', 0.0],
     ['TotalCredit',0.0],
     ['TotalDebet',0.0],
     ['EndBalance',0.0],
  )

  # Get Beginning Balance
  oCashAccount = helper.GetObject('CashAccount',AccountNo)
  recSaldo.BeginningBalance = oCashAccount.GetBalanceByDate(int(BeginDate))
  recSaldo.CashAccountNo = oCashAccount.AccountNo
  recSaldo.CashAccountName = oCashAccount.AccountName
  recSaldo.CashAccountBranch = oCashAccount.LBranch.BranchName
  recSaldo.CashAccountCurrency = oCashAccount.LCurrency.Short_Name

  # Get Detail Transaction
  dsHist = returns.AddNewDatasetEx(
    'histori',
    ';'.join([
      'TransactionItemId: integer',
      'TransactionDate: datetime',
      'TransactionDateStr: string',
      'TransactionCode: string',
      'MutationType: string',
      'Amount: float',
      'Balance:float',
      'ReferenceNo: string',
      'Description: string',
      'Inputer: string',
      'TransactionNo: string',
      'AuthStatus: string',
    ])
  )

  s = ' \
    SELECT FROM AccountTransactionItem \
    [ \
      AccountNo = :AccountNo and \
      LTransaction.ActualDate >= :BeginDate and \
      LTransaction.ActualDate <= :EndDate \
    ] \
    ( \
      TransactionItemId, \
      LTransaction.ActualDate, \
      LTransaction.TransactionCode, \
      MutationType, \
      Amount, \
      LTransaction.ReferenceNo, \
      LTransaction.Description, \
      LTransaction.Inputer, \
      LTransaction.TransactionNo, \
      LTransaction.AuthStatus,\
      Self \
    ) \
    THEN ORDER BY ASC ActualDate, ASC TransactionItemId;'

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('AccountNo', AccountNo)
  oql.SetParameterValueByName('BeginDate', int(BeginDate))
  oql.SetParameterValueByName('EndDate', int(EndDate) + 1)
  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  Balance = recSaldo.BeginningBalance
  TotalCredit = 0.0
  TotalDebet = 0.0
  while not ds.Eof:
    recHist = dsHist.AddRecord()
    recHist.TransactionItemId = ds.TransactionItemId
    recHist.TransactionDate = AsDateTime(ds.ActualDate)
    recHist.TransactionDateStr = config.FormatDateTime('dd-mmm-yyyy',recHist.TransactionDate)
    recHist.TransactionCode = ds.TransactionCode
    recHist.MutationType = ds.MutationType
    if ds.MutationType == 'D':
      Balance += ds.Amount
      TotalDebet += ds.Amount
    else:
      Balance -= ds.Amount
      TotalCredit += ds.Amount
      
    # end if
    recHist.Balance = Balance
    recHist.Amount = ds.Amount
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description
    recHist.Inputer = ds.Inputer
    recHist.TransactionNo = ds.TransactionNo
    recHist.AuthStatus = AUTHSTATUS[ds.AuthStatus]

    ds.Next()
  #-- while
  recSaldo.TotalCredit = TotalCredit
  recSaldo.TotalDebet = TotalDebet
  recSaldo.EndBalance = recSaldo.BeginningBalance - TotalCredit + TotalDebet

def PrintHistTransaction(config, params, returns):
  def AsString(tdate):
    return ('%s-%s-%s' % (str(tdate[2]), str(tdate[1]), str(tdate[0])))

  helper = phelper.PObjectHelper(config)
  app = config.AppObject

  status = returns.CreateValues(
      ['Is_Err',0],['Err_Message','']
  )

  rec = params.FirstRecord
  AccountNo = rec.AccountNo
  BeginDate = rec.BeginDate
  EndDate   = rec.EndDate

  oAccount = helper.GetObject('CashAccount',AccountNo).CastToLowestDescendant()
  Header = 'HISTORI TRANSAKSI '
  if oAccount.IsA('BankCash'):
    Header += 'REKENING BANK'
  elif oAccount.IsA('PettyCash'):
    Header += 'KAS KECIL'
  elif oAccount.IsA('BranchCash'):
    Header += 'KAS CABANG'
  else:
    Header += ''

  # Get Info Cabang
  corporate = helper.CreateObject('Corporate')
  CabangInfo = corporate.GetCabangInfo(oAccount.BranchCode)
  Cabang = '%s - %s' % (oAccount.BranchCode,CabangInfo.Nama_Cabang)

  # Get Info Valuta

  res = app.rexecscript('accounting','appinterface/Currency.GetCurrencyInfo',
        app.CreateValues(['kode_valuta',oAccount.CurrencyCode]))

  rec = res.FirstRecord
  if rec.Is_Error : raise '',rec.Err_Message
  Valuta = '%s - %s' % (oAccount.CurrencyCode,rec.short_name)

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
      LTransaction.Inputer, \
      Self \
    ) \
    THEN ORDER BY ASC TransactionDate, ASC TransactionItemId;'

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('AccountNo', AccountNo)
  oql.SetParameterValueByName('BeginDate', int(BeginDate))
  oql.SetParameterValueByName('EndDate', int(EndDate) + 1)
  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  # Prepare Excel Object
  PrintHelper = helper.CreateObject('PrintHelper')
  workbook = PrintHelper.LoadExcelTemplate('CashAccountHistory')
  try :
    workbook.ActivateWorksheet('data')


    workbook.SetCellValue(1, 1, Header)
    workbook.SetCellValue(2, 3, oAccount.AccountNo)
    workbook.SetCellValue(3, 3, oAccount.AccountName)
    workbook.SetCellValue(4, 3, Cabang)
    workbook.SetCellValue(5, 3, Valuta)
    row = 8
    while not ds.Eof:
      workbook.SetCellValue(row, 1, str(row - 5) )
      workbook.SetCellValue(row, 2, AsString(ds.TransactionDate))
      workbook.SetCellValue(row, 3, ds.Amount)
      workbook.SetCellValue(row, 4, ds.Description)

      row += 1
      ds.Next()
    # end while

    # save report file
    FileName = 'CashAccountHistory.xls'
    corporate = helper.CreateObject('Corporate')
    FullName = corporate.GetUserHomeDir() + '\\' + FileName
    if os.access(FullName, os.F_OK) == 1:
        os.remove(FullName)
    workbook.SaveAs(FullName)


    sw = returns.AddStreamWrapper()
    sw.LoadFromFile(FullName)
    sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(FullName)

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
  # try except

  workbook = None
  #-- while
