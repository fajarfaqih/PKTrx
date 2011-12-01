import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.labs.m_textreport as textreport
import sys

def DAFScriptMain(config, params, returns):
  return 1

def PrintText(config, params, returns):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  helper = phelper.PObjectHelper(config)    
  param = params.FirstRecord

  sw = returns.AddStreamWrapper()
  reportFile = PrintReport(helper, config, param)
  
  
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
    ['PeriodDate',''],
    ['Branch',''],
    ['TotalBeginBalance',0.0],
    ['TotalDebet',0.0],
    ['TotalCredit',0.0],
    ['TotalEndBalance',0.0],                
  )
  dsData = returns.AddNewDatasetEx(
    'ReportData',
    ';'.join([
      'AccountName : string',
      'CurrencyName : string',
      'Rate : float',      
      'Debet : float',      
      'Credit : float',
      'Total : float',                  
      'BeginBalance : float',
      'EndBalance : float',
    ])
  )
  
  try:
    # BRANCH NAME
    corporate = helper.CreateObject('Corporate')
    CabangInfo = corporate.GetCabangInfo(param.BranchCode) 
    status.Branch = '%s - %s' % (param.BranchCode,CabangInfo.Nama_Cabang)
  
    # DATE
    aBeginDate = param.BeginDate
    aEndDate = param.EndDate
    status.PeriodDate = "%s s/d %s" % (config.FormatDateTime('dd-mm-yyyy', aBeginDate),
                              config.FormatDateTime('dd-mm-yyyy', aEndDate))
     
                 
    sSQL = BuildSQLSummaryCash(config,aBeginDate,aEndDate,param.BranchCode)
    
    status.TotalBeginBalance = 0.0
    status.TotalEndBalance = 0.0
    status.TotalDebet = 0.0
    status.TotalCredit = 0.0
    
    res = config.CreateSQL(sSQL).rawresult
    while not res.Eof:      
      aDebit   = res.Debit or 0.0
      aDebitEkuiv = res.DebitEkuiv or 0.0
      aCredit  = res.Credit or 0.0
      aCreditEkuiv = res.CreditEkuiv or 0.0
      aBegin   = res.BeginBalance or 0.0
      aBeginEkuiv = res.BeginBalanceEkuiv or 0.0
      
      oCashAccount = helper.GetObject('CashAccount',res.AccountNo)
      Rate = oCashAccount.LCurrency.Kurs_Tengah_BI
            
      status.TotalBeginBalance += aBeginEkuiv
      status.TotalDebet += aDebitEkuiv
      status.TotalCredit += aCreditEkuiv
            
      recData = dsData.AddRecord()      
      recData.AccountName     = '%s - %s' % ( res.AccountNo,oCashAccount.AccountName )
      recData.CurrencyName = oCashAccount.LCurrency.Short_Name
      #recData.Rate = Rate      
      recData.Debet       = aDebit 
      recData.Credit      = aCredit
      recData.Total       = aDebit - aCredit  
      recData.BeginBalance = aBegin
      recData.EndBalance  = aBegin + aDebit - aCredit
      
      status.TotalEndBalance += (aBeginEkuiv + aDebitEkuiv - aCreditEkuiv )

      res.Next()
    # end while
    
        
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

def PrintReport(helper, config, param):
  corporate = helper.CreateObject('Corporate')
  
  reportdef = config.HomeDir + 'reports/summarycash.mtr'
  oReport = textreport.TextReport(reportdef)  
  
  # Set HEADER

  # Set BRANCH
  aBranchCode = param.BranchCode
  CabangInfo = corporate.GetCabangInfo(param.BranchCode)
  Cabang = '%s - %s' % (param.BranchCode,CabangInfo.Nama_Cabang)
  oReport.SetVars('BRANCH', Cabang)
  
  # Set DATE PERIOD
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
  
  # Set Begin Balance
  resBeginBalance = config.CreateSQL(BuildSQLSummaryCashBalance( aBranchCode, aBeginDateParam)).rawresult
  aBeginBalance = resBeginBalance.Total or 0.0
  oReport.SetVars('BEGINBALANCE', config.FormatFloat(',0.00', aBeginBalance))
  
  # Set Total Debet
  resDebet = config.CreateSQL( BuildSQLSummaryCashTotal( aBranchCode, aBeginDateParam, aEndDateParam, 'D')).rawresult
  TotalDebet = resDebet.Total or 0.0
  oReport.SetVars('TOTALDEBET', config.FormatFloat(',0.00', TotalDebet))
  
  # Set Total Credit
  resCredit = config.CreateSQL( BuildSQLSummaryCashTotal( aBranchCode, aBeginDateParam, aEndDateParam, 'C')).rawresult
  TotalCredit = resCredit.Total or 0.0
  oReport.SetVars('TOTALCREDIT', config.FormatFloat(',0.00',  TotalCredit))
  
  # Set End Balance
  oReport.SetVars('ENDBALANCE', config.FormatFloat(',0.00', aBeginBalance + TotalDebet - TotalCredit ))

  # Set nama file output.txt
  
  reportFile = corporate.GetUserHomeDir() + '\\Rep_SummaryCash.txt'
  oReport.OpenReport(reportFile)
  
  try:
    
    sSQL = BuildSQLSummaryCash(config,aBeginDate,aEndDate,param.BranchCode)
    
    res = config.CreateSQL(sSQL).rawresult

    while not res.Eof:
      aContent = {}

      oCashAccount = helper.GetObject('CashAccount',res.AccountNo)
      
      aDebit   = res.Debit or 0.0
      aCredit  = res.Credit or 0.0
      aBegin   = res.BeginBalance or 0.0
        
        
      aContent['ACCOUNT']     = ('%s - %s' % ( res.AccountNo,oCashAccount.AccountName ))[:39]
      aContent['CURRENCYNAME'] = oCashAccount.LCurrency.Short_Name
      aContent['DEBIT']       = config.FormatFloat(',0.00', aDebit) 
      aContent['CREDIT']      = config.FormatFloat(',0.00', aCredit)
      aContent['TOTAL']       = config.FormatFloat(',0.00', aDebit - aCredit)
      aContent['BEGINBALANCE'] = config.FormatFloat(',0.00', aBegin)
      aContent['ENDBALANCE']  = config.FormatFloat(',0.00', aBegin + aDebit - aCredit)
      
      oReport.PrintRow('detail', aContent)
       
      res.Next()
    #-- while
    
  finally:
    oReport.Close()
  
  return reportFile
  
def BuildSQLSummaryCash(config,aBeginDate,aEndDate,aBranchCode):
    qParam = {}
    qParam['BEGIN'] = config.FormatDateTime('yyyy-mm-dd', aBeginDate)
    qParam['END'] = config.FormatDateTime('yyyy-mm-dd', aEndDate)
    qParam['BRANCH'] = aBranchCode
    
    return "\
      select a.AccountNo,f.CurrencyCode,  \
      	sum(case when MutationType = 'D' and \
          ActualDate >= '%(BEGIN)s' then i.Amount else 0.0 end) as Debit,\
        sum(case when MutationType = 'D' and \
          ActualDate >= '%(BEGIN)s' then i.EkuivalenAmount else 0.0 end) as DebitEkuiv,\
      	sum(case when MutationType = 'C' and \
          ActualDate >= '%(BEGIN)s' then i.Amount else 0.0 end) as Credit,\
        sum(case when MutationType = 'C' and \
          ActualDate >= '%(BEGIN)s' then i.EkuivalenAmount else 0.0 end) as CreditEkuiv,\
      	sum(case when MutationType = 'D' and \
            ActualDate < '%(BEGIN)s' then i.Amount\
          when MutationType = 'C' and \
            ActualDate < '%(BEGIN)s' then -i.Amount\
      			else 0.0 end) as BeginBalance , \
        sum(case when MutationType = 'D' and \
            ActualDate < '%(BEGIN)s' then i.EkuivalenAmount\
          when MutationType = 'C' and \
            ActualDate < '%(BEGIN)s' then -i.EkuivalenAmount\
            else 0.0 end) as BeginBalanceEkuiv \
      from \
      	accounttransactionitem a, transactionitem i, cashaccount c, \
      	financialaccount f, transaction t	\
      where a.TransactionItemId = i.TransactionItemId \
      	and a.AccountNo = c.AccountNo and c.AccountNo = f.AccountNo \
      	and i.TransactionId = t.TransactionId \
      	and t.ActualDate <= '%(END)s' \
      	and i.BranchCode = '%(BRANCH)s' \
      group by a.AccountNo,f.CurrencyCode \
      order by CurrencyCode,AccountNo \
    " % qParam 

def BuildSQLSummaryCashBalance(aBranchCode, aBeginDateParam):
     
  return "\
        select sum(case when i.mutationtype='D' then i.EkuivalenAmount \
                           else -i.EkuivalenAmount \
                      end) as Total \
        from accounttransactionitem a,  cashaccount c, financialaccount f, \
          transaction t , transactionitem i \
        where a.TransactionItemId = i.TransactionItemId \
          and i.TransactionId = t.TransactionId \
          and f.accountno = c.accountno \
          and a.accountno = c.accountno \
          and t.ActualDate < '%s' \
          and f.BranchCode = '%s' \
      " % ( aBeginDateParam, aBranchCode)
          
def BuildSQLSummaryCashTotal(aBranchCode, aBeginDateParam, aEndDateParam,aMutationType ):
  AddParam = ""

  if aMutationType != None :
    AddParam += " and i.MutationType='%s' " % aMutationType
     
  return "\
        select sum(i.EkuivalenAmount) as Total \
        from accounttransactionitem a,  cashaccount c, financialaccount f, \
          transaction t , transactionitem i \
        where a.TransactionItemId = i.TransactionItemId \
          and i.TransactionId = t.TransactionId \
          and f.accountno = c.accountno \
          and a.accountno = c.accountno \
          and t.ActualDate >= '%s' \
          and t.ActualDate <= '%s' \
          and f.BranchCode = '%s' \
          %s \
      " % ( aBeginDateParam, aEndDateParam, aBranchCode, AddParam)