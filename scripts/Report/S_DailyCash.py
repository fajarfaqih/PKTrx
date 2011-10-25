import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.labs.m_textreport as textreport
import sys

def DAFScriptMain(config, params, returns):  
  return 1

AUTHSTATUS = {'T' : 'SUDAH OTORISASI','F':'BELUM OTORISASI'}
  
def PrintText(config, params, returns):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  helper = phelper.PObjectHelper(config)    
  param = params.FirstRecord
  
  sw = returns.AddStreamWrapper()
  reportFile = GetTextReport(helper, config, param)
  
  sw.LoadFromFile(reportFile)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(reportFile)

  return 1

def PrintExcel(config, params, returns):
  app = config.AppObject
  helper = phelper.PObjectHelper(config)

  param = params.FirstRecord
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['StrDate',''],
    ['CashName',''],
    ['Branch',''],
    ['Currency',''],
    ['BeginBalance',0.0],
    ['TotalDebet',0.0],
    ['TotalCredit',0.0],        
    ['EndBalance',0.0],        
  )
  dsData = returns.AddNewDatasetEx(
    'ReportData',
    ';'.join([
      'BatchNo : string',
      'TransactionDateStr : string',
      'MutationType : string',
      'Amount : float',
      'Balance : float',
      'ReferenceNo : string',      
      'Inputer : string',
      'Description : string',
      'AuthStatus : string',
      'TransactionNo : string',
    ])
  )
  
  try:
    # BRANCH NAME
    corporate = helper.CreateObject('Corporate')
    CabangInfo = corporate.GetCabangInfo(param.BranchCode) 
    status.Branch = '%s - %s' % (param.BranchCode,CabangInfo.Nama_Cabang)
    
    # CURRENCY NAME
    accountNo = param.GetFieldByName('LCashAccount.AccountNo')
    accountName = param.GetFieldByName('LCashAccount.AccountName')
    currencyCode = param.GetFieldByName('LCashAccount.CurrencyCode')        
    res = app.rexecscript('accounting','appinterface/Currency.GetCurrencyInfo',
          app.CreateValues(['kode_valuta',currencyCode]))
    rec = res.FirstRecord
    if rec.Is_Error : raise '',rec.Err_Message 
    status.Currency = '%s - %s' % (currencyCode,rec.full_name)
  
    # DATE
    aBeginDate = param.BeginDate
    aEndDate = param.EndDate    
    aBeginDateParam = config.FormatDateTime('yyyy-mm-dd', aBeginDate)
    aEndDateParam = config.FormatDateTime('yyyy-mm-dd', aEndDate)
    if aBeginDate == aEndDate:
      status.StrDate = config.FormatDateTime('dd-mm-yyyy', aBeginDate)
    else:    
      status.StrDate = '%s - %s' % (
                 config.FormatDateTime('dd/mm/yyyy', aBeginDate),
                 config.FormatDateTime('dd/mm/yyyy', aEndDate) 
               )    
     
    # BALANCE INFO 
    aBeginBalance, aEndBalance = 0.0, 0.0
    oService = helper.LoadScript('Account.Balance')
    if param.IsAllCash == 'F':
      aBeginBalance, aEndBalance = oService.GetDayBalance(config, 
        {'AccountNo': accountNo, 'Date': aBeginDate})
        
    status.BeginBalance = aBeginBalance

    resDebet = config.CreateSQL(BuildSumSQLSelectedCash(accountNo, aBeginDateParam, aEndDateParam,'D')).rawresult
    status.TotalDebet = resDebet.Total or 0.0    
    resCredit = config.CreateSQL(BuildSumSQLSelectedCash(accountNo, aBeginDateParam, aEndDateParam,'C')).rawresult
    status.TotalCredit = resCredit.Total or 0.0    
    status.EndBalance = aBeginBalance + status.TotalDebet - status.TotalCredit
    
    Balance = aBeginBalance                 
    sSQL = BuildSQLSelectedCash(accountNo, aBeginDateParam, aEndDateParam)
    res = config.CreateSQL(sSQL).rawresult
    while not res.Eof:      
      recData = dsData.AddRecord()      
      aDate = res.ActualDate  
      recData.TransactionDateStr = '%2s-%2s-%4s' % (str(aDate[2]).zfill(2), 
                                                 str(aDate[1]).zfill(2), 
                                                 str(aDate[0]))
      recData.BatchNo = res.BatchNo                                           
      recData.ReferenceNo = res.ReferenceNo
      recData.Amount = res.Amount
      if res.MutationType == 'D':
        Balance += res.Amount
      else:
        Balance -= res.Amount
      
      recData.Balance = Balance
      recData.MutationType = res.MutationType
      recData.Description = res.Description     
      recData.Inputer = res.Inputer
      recData.Authstatus  = AUTHSTATUS[res.AuthStatus]
      recData.TransactionNo = res.TransactionNo
            
      res.Next()
    # end while
        
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

  
def GetTextReport(helper, config, param):
  corporate = helper.CreateObject('Corporate')
  app = config.AppObject
  
  reportdef = config.HomeDir + 'reports/dailycash.mtr'
  oReport = textreport.TextReport(reportdef)  
  
  # Set Title

  CabangInfo = corporate.GetCabangInfo(param.BranchCode)
  Cabang = '%s - %s' % (param.BranchCode,CabangInfo.Nama_Cabang)
  oReport.SetVars('BRANCH', Cabang)
  if param.IsAllCash == 'T':
    oReport.SetVars('CASHACCOUNT', 'SEMUA KAS')
    currencyCode = param.GetFieldByName('LCashAccount.CurrencyCode')
    if currencyCode == None: currencyCode = '000'
    oReport.SetVars('CURRENCY', currencyCode)
  else:
    accountNo = param.GetFieldByName('LCashAccount.AccountNo')
    accountName = param.GetFieldByName('LCashAccount.AccountName')
    oReport.SetVars('CASHACCOUNT', '%s %s' % (accountNo, accountName))
    currencyCode = param.GetFieldByName('LCashAccount.CurrencyCode')
    
    
  res = app.rexecscript('accounting','appinterface/Currency.GetCurrencyInfo',
        app.CreateValues(['kode_valuta',currencyCode]))
  rec = res.FirstRecord
  if rec.Is_Error : raise '',rec.Err_Message
  Valuta = '%s - %s' % (currencyCode,rec.full_name)
  oReport.SetVars('CURRENCY', Valuta)
  
  aBeginDate = param.BeginDate
  aEndDate = param.EndDate    
  aBeginDateParam = config.FormatDateTime('yyyy-mm-dd', aBeginDate)
  aEndDateParam = config.FormatDateTime('yyyy-mm-dd', aEndDate)
  
  if aBeginDate == aEndDate:
   TransactionDateStr = config.FormatDateTime('dd-mm-yyyy', aBeginDate)
  else:    
   TransactionDateStr = '%s - %s' % (
               config.FormatDateTime('dd/mm/yyyy', aBeginDate),
               config.FormatDateTime('dd/mm/yyyy', aEndDate) 
             )
  oReport.SetVars('DATE', TransactionDateStr)
  
  aBeginBalance, aEndBalance = 0.0, 0.0
  oService = helper.LoadScript('Account.Balance')
  if param.IsAllCash == 'F':
    aBeginBalance, aEndBalance = oService.GetDayBalance(config, 
      {'AccountNo': accountNo, 'Date': aBeginDate})
      
  oReport.SetVars('BEGINBALANCE', config.FormatFloat(',0.00', aBeginBalance))
  
  resDebet = config.CreateSQL(BuildSumSQLSelectedCash(accountNo, aBeginDateParam, aEndDateParam,'D')).rawresult
  TotalDebet = resDebet.Total or 0.0
  oReport.SetVars('TOTALDEBET', config.FormatFloat(',0.00', TotalDebet))
  
  resCredit = config.CreateSQL(BuildSumSQLSelectedCash(accountNo, aBeginDateParam, aEndDateParam,'C')).rawresult
  TotalCredit = resCredit.Total or 0.0
  oReport.SetVars('TOTALCREDIT', config.FormatFloat(',0.00',  TotalCredit))
  oReport.SetVars('ENDBALANCE', config.FormatFloat(',0.00', aBeginBalance + TotalDebet - TotalCredit ))
  
  # Set nama file output.txt
  reportFile = corporate.GetUserHomeDir() + '\\Rep_DailyCash.txt'
  oReport.OpenReport(reportFile)

  try:        
    if param.IsAllCash == 'T':      
      sSQL = BuildSQLAllCash(aDateParam, param.BranchCode, currencyCode)
    else:            
      sSQL = BuildSQLSelectedCash(accountNo, aBeginDateParam, aEndDateParam)
    # end if      
    
    res = config.CreateSQL(sSQL).rawresult
    while not res.Eof:
      aContent = {}
      aTime = res.ActualDate
      aContent['TIME']        = '%2s:%2s:%2s' % (str(aTime[3]).zfill(2), str(aTime[4]).zfill(2), str(aTime[5]).zfill(2))
      aContent['BATCHNO']     = res.BatchNo
      aContent['MUTASI']      = res.MutationType
      aContent['AMOUNT']      = config.FormatFloat(',0.00', res.Amount)
      aContent['REFERENCE']   = res.ReferenceNo
      aContent['INPUTER']     = res.Inputer
      aContent['DESCRIPTION'] = res.Description
      aContent['AUTHSTATUS']  = res.AuthStatus
      
      oReport.PrintRow('detail', aContent)
       
      res.Next()
    #-- while
    
  finally:
    oReport.Close()
  
  return reportFile

def BuildSQLAllCash(aDateParam, aBranchCode, aCurrencyCode):
  return "\
        select t.ActualDate, b.BatchNo, a.AccountNo, \
          i.MutationType, i.Amount, t.ReferenceNo, t.Inputer, \
          t.Description, t.AuthStatus,i.TransactionItemId \
        from accounttransactionitem a, transactionitem i, \
          transaction t, transactionbatch b, cashaccount c \
        where a.TransactionItemId = i.TransactionItemId \
          and a.AccountNo = c.AccountNo \
          and i.TransactionId = t.TransactionId \
          and t.BatchId = b.BatchId \
          and t.ActualDate = '%s' \
          and i.BranchCode = '%s' \
          and i.CurrencyCode = '%s' \
        order by ActualDate,TransactionItemId \
      " % (aDateParam, aBranchCode, aCurrencyCode)
  pass
      
def BuildSQLSelectedCash(aAccountNo, aBeginDateParam, aEndDateParam):
  return "\
        select t.ActualDate, b.BatchNo, a.AccountNo, \
          i.MutationType, i.Amount, t.ReferenceNo, t.Inputer, \
          t.Description, t.AuthStatus,i.TransactionItemId, t.TransactionNo \
        from accounttransactionitem a, transactionitem i, \
          transaction t, transactionbatch b \
        where a.TransactionItemId = i.TransactionItemId \
          and a.AccountNo = '%s' \
          and i.TransactionId = t.TransactionId \
          and t.BatchId = b.BatchId \
          and t.ActualDate >= '%s' \
          and t.ActualDate <= '%s' \
        order by ActualDate,TransactionItemId \
      " % (aAccountNo, aBeginDateParam, aEndDateParam)
      
def BuildSumSQLSelectedCash(aAccountNo, aBeginDateParam, aEndDateParam,aMutationType):
  return "\
        select sum(i.Amount) as Total \
        from accounttransactionitem a, transactionitem i, \
          transaction t, transactionbatch b \
        where a.TransactionItemId = i.TransactionItemId \
          and a.AccountNo = '%s' \
          and i.TransactionId = t.TransactionId \
          and t.BatchId = b.BatchId \
          and t.ActualDate >= '%s' \
          and t.ActualDate <= '%s' \
          and i.MutationType='%s' \
      " % (aAccountNo, aBeginDateParam, aEndDateParam, aMutationType)