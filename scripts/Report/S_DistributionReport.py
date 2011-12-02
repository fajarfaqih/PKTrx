import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.labs.m_textreport as textreport
import sys  

addFilter = ""

def DAFScriptMain(config,parameters,returns):
  helper = phelper.PObjectHelper(config)

  param = parameters.FirstRecord
  
  sw = returns.AddStreamWrapper()
  reportFile = PrintReport(helper, config, param)
  
  sw.LoadFromFile(reportFile)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(reportFile)

def GetDataTransaction(config,parameters,returns):
  helper = phelper.PObjectHelper(config)

  param = parameters.FirstRecord
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['Cabang',''],
    ['Tanggal',''],
    ['TotalAmount',0.0],
  )
  dsData = returns.AddNewDatasetEx(
    'ReportData',
    ';'.join([
      'TransactionDate: datetime',
      'TransactionDateStr: string',
      'InputDateStr:string',
      'ReferenceNo: string',      
      'AccountName: string',
      'Description: string',
      'Amount: float',
      'Rate: float',
      'EkuivalenAmount: float',
      'AuthStatus: string',
      'Channel:string',
      'FundEntity: string',
      'SponsorName: string',
      'Inputer: string',
      'BranchName: string',
      'TransactionNo: string',
      'CurrencyName: string',
    ])
  )
  
  try:
    corporate = helper.CreateObject('Corporate')
    BranchCode = None
    Cabang = '' 
    if param.IsAllBranch == 'F' :
      BranchCode = param.GetFieldByName('LBranch.BranchCode')
      CabangInfo = corporate.GetCabangInfo(BranchCode)
      Cabang = '%s - %s' % (BranchCode,CabangInfo.Nama_Cabang)    
    
    aBeginDate = param.BeginDate
    aEndDate = param.EndDate
      
    if aBeginDate == aEndDate:
       Tanggal = '%s' % config.FormatDateTime('dd mmm yyyy', aBeginDate)
    else:    
       Tanggal = '%s s/d %s' % (
                   config.FormatDateTime('dd mmm yyyy', aBeginDate),
                   config.FormatDateTime('dd mmm yyyy', aEndDate) 
                 )
                 
    data = GetData(config,param)
    TotalAmount = 0.0
    while not data.Eof:
      recData = dsData.AddRecord()
      aDate = data.ActualDate  
      recData.TransactionDateStr = '%2s-%2s-%4s' % (str(aDate[2]).zfill(2), 
                                                 str(aDate[1]).zfill(2), 
                                                 str(aDate[0]))
      aDate = data.TransactionDate
      recData.InputDateStr = '%2s-%2s-%4s' % (str(aDate[2]).zfill(2), 
                                                 str(aDate[1]).zfill(2), 
                                                 str(aDate[0]))
                                                 
      recData.ReferenceNo = data.ReferenceNo
      recData.AccountName = data.AccountName
      recData.Description = data.Description

      Amount , Rate, CurrencyName = GetAmount(data)
      recData.CurrencyName = CurrencyName #CURRSYMBOL[res.CurrencyCode]
      recData.Rate         = Rate
      recData.Amount       = Amount

      #recData.Amount = data.Amount
      recData.EkuivalenAmount = data.EkuivalenAmount
      TotalAmount += data.EkuivalenAmount
      recData.Inputer = data.Inputer
      recData.Authstatus  = data.AuthStatus
      recData.Channel  = data.Channel[:20]
      recData.FundEntity = data.FundEntity
      recData.SponsorName = ''
      recData.BranchName = data.BranchName
      recData.TransactionNo = data.TransactionNo
            
      data.Next()
    # end while
    status.TotalAmount = TotalAmount    
        # Get SponsorName
  #       SName = ''
  #       oST = helper.GetObject('SponsorTransaction',res.TransactionItemId)
  #       if not oST.isnull :
  #          SName = oST.LSponsor.Name
  #       aContent['SPONSORNAME'] = SName[:19]
    
    status.Cabang = Cabang
    status.Tanggal = Tanggal
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
        
def GetAmount(res):
  if res.CurrencyCode != res.TransCurrencyCode and res.CurrencyCode == '000':
    CurrencyName = res.TransCurrencyName #CURRSYMBOL[res.TransCurrencyCode]
    Rate         = res.TransRate
    Amount       = res.Amount / res.TransRate
  else :
    CurrencyName = res.CurrencyName #CURRSYMBOL[res.CurrencyCode]
    Rate         = res.Rate
    Amount       = res.Amount
  # end if
  return Amount , Rate, CurrencyName 

def GetData(config,param):
  global addFilter

  aBeginDate = param.BeginDate
  aEndDate = param.EndDate
  aBranchCode = param.GetFieldByName('LBranch.BranchCode')  
  aHeadOfficeCode = config.SysVarIntf.GetStringSysVar('OPTION','HeadOfficeCode')
  IsHeadOffice = (aBranchCode == aHeadOfficeCode)
  
  addFilter = ""
  addFilter2 = ""
  if param.IsAllDonor == 'F' :
    addFilter += " and exists ( \
                      select 1 from transaction.transactionitem st , \
                      transaction.accounttransactionitem sa \
                      where st.transactionitemid=sa.transactionitemid \
                      and sa.donorid=%d and st.transactionid= t.transactionid \
                   ) " % param.IdDonor            
    addFilter2 += " and false"

  if param.IsAllBranch == 'F' :
    addFilter += " and i.BranchCode='%s' " % aBranchCode
    addFilter2 += " and i.BranchCode='%s' " % aBranchCode      
  else : # Show All Branch
    if not IsHeadOffice :
      UserBranchCode = config.SecurityContext.GetUserInfo()[4]
      SQLParam = "and ( b.BranchCode='%(BranchCode)s'  or b.MasterBranchCode='%(BranchCode)s' ) " 
      addFilter += SQLParam % {'BranchCode' : UserBranchCode}
      addFilter2 += SQLParam % {'BranchCode' : UserBranchCode}
      
      
  if param.IsAllChannel == 'F' :
    addFilter += " and t.ChannelCode='%s' " % param.ChannelCode
    addFilter2 += " and t.ChannelCode='%s' " % param.ChannelCode
          
  if param.IsAllProgram == 'F' : 
    addFilter += " and f.AccountNo='%s' " % param.AccountNo
    addFilter2 += " and false"

  if param.IsAllSponsor == 'F' :      
    addFilter += " and exists ( \
                       select 1 from sponsortransaction sp \
                       where sp.transactionitemid = i.transactionitemid \
                         and sp.SponsorId=%d \
                    ) " % param.IdDonor
    addFilter2 += " and false"                     

  if param.IsAllVolunteer == 'F' :      
    addFilter += " and exists ( \
                      select 1 from volunteertransaction vt \
                      where vt.transactionitemid = i.transactionitemid \
                        and vt.VolunteerId='%s' \
                   ) " % param.GetFieldByName('LVolunteer.VolunteerId')
    addFilter2 += " and false"                          

  if param.IsAllFundEntity == 'F' :
    addFilter += " and a.FundEntity='%s' " % param.FundEntity
    if param.FundEntity != 4:
      addFilter2 += " and false"
  
  qParam = {}
  qParam['BDATE'] = config.FormatDateTime('yyyy-mm-dd', aBeginDate) 
  qParam['EDATE'] = config.FormatDateTime('yyyy-mm-dd', aEndDate) 
  
  qParam['BRANCH'] = param.BranchCode
  qParam['CURRENCY'] = '000'
  qParam['ADDFILTER'] = addFilter
  qParam['ADDFILTER2'] = addFilter2
  
     
  sSQL = "\
      select t.TransactionDate,t.ActualDate, t.ReferenceNo, f.AccountName, \
        t.Description, i.Amount,i.Rate,i.Ekuivalenamount, i.CurrencyCode, t.Inputer,t.donorname, \
        t.AuthStatus, t.TransactionId,  \
        (case when t.ChannelCode = 'R' then 'Kas Cabang' \
              when t.ChannelCode = 'P' then 'Kas Kecil' \
              when t.ChannelCode = 'A' then 'Bank' else 'Aktiva' end) as Channel ,\
        (case when a.FundEntity = '1' then 'Zakat' \
              when a.FundEntity = '2' then 'Infaq' \
              when a.FundEntity = '3' then 'Wakaf' \
              when a.FundEntity = '4' then 'Amil' \
              when a.FundEntity = '5' then 'Lainnya' \
              else '' end) as FundEntity, \
         i.transactionitemid , b.branchname, t.TransactionNo ,\
         t.currencycode as TransCurrencyCode , t.rate as TransRate , \
         (select short_name from currency c where c.currency_code = i.currencycode) as CurrencyName , \
            (select short_name from currency c where c.currency_code = t.currencycode) as TransCurrencyName \
      from accounttransactionitem a, transactionitem i, \
        transaction t, financialaccount f , productaccount p ,branch b\
      where a.TransactionItemId = i.TransactionItemId \
        and i.TransactionId = t.TransactionId \
        and p.AccountNo=f.AccountNo \
        and a.AccountNo = f.AccountNo \
        and f.AccountNo = p.AccountNo \
        and b.branchcode = i.branchcode \
        and t.TransactionCode in ('DD001','CAR','EAR','FA','GT') \
        and t.ActualDate >= '%(BDATE)s' \
        and t.ActualDate <= '%(EDATE)s' \
        and i.MutationType = 'D' \
        %(ADDFILTER)s \
    " % qParam
  
  sSQL += " union \
      select t.TransactionDate,t.ActualDate, t.ReferenceNo, f.AccountName, \
        t.Description, i.Amount,i.Rate,i.Ekuivalenamount, i.CurrencyCode, t.Inputer,t.donorname, \
        t.AuthStatus, t.TransactionId,  \
        (case when t.ChannelCode = 'R' then 'Kas Cabang' \
              when t.ChannelCode = 'P' then 'Kas Kecil' \
              when t.ChannelCode = 'A' then 'Bank' else 'Aktiva' end) as Channel ,\
        (case when a.FundEntity = '1' then 'Zakat' \
              when a.FundEntity = '2' then 'Infaq' \
              when a.FundEntity = '3' then 'Wakaf' \
              when a.FundEntity = '4' then 'Amil' \
              when a.FundEntity = '5' then 'Lainnya' \
              else '' end) as FundEntity, \
         i.transactionitemid , b.branchname, t.TransactionNo , \
         t.currencycode as TransCurrencyCode , t.rate as TransRate , \
         (select short_name from currency c where c.currency_code = i.currencycode) as CurrencyName , \
         (select short_name from currency c where c.currency_code = t.currencycode) as TransCurrencyName \
      from accounttransactionitem a, transactionitem i, \
        transaction t, financialaccount f , productaccount p ,branch b\
      where a.TransactionItemId = i.TransactionItemId \
        and i.TransactionId = t.TransactionId \
        and p.AccountNo=f.AccountNo \
        and a.AccountNo = f.AccountNo \
        and f.AccountNo = p.AccountNo \
        and b.branchcode = i.branchcode \
        and t.TransactionCode in ('CA') \
        and t.ActualDate >= '%(BDATE)s' \
        and t.ActualDate <= '%(EDATE)s' \
        and i.MutationType = 'D' \
        and not exists(select 1 from cashadvancereturninfo c where c.SourceTransactionId=t.TransactionId) \
        %(ADDFILTER)s \
    " % qParam
        
#   sSQL += " union \
#       select t.TransactionDate,t.ActualDate, t.ReferenceNo, a.account_name as AccountName, \
#         t.Description, i.Amount,i.Rate,i.Ekuivalenamount, t.Inputer, '' as donorname, \
#         t.AuthStatus, t.TransactionId, \
#         (case when t.ChannelCode = 'R' then 'Kas Cabang' \
#               when t.ChannelCode = 'P' then 'Kas Kecil' \
#               when t.ChannelCode = 'A' then 'Bank' else 'Aktiva' end) as Channel , \
#         'Amil' as FundEntity, \
#          i.transactionitemid , b.branchname , t.TransactionNo\
#       from transaction.transaction t, transaction.transactionitem i, \
#         accounting.account a ,branch b\
#       where t.transactionid = i.transactionid \
#         and b.branchcode = i.branchcode \
#         and t.transactioncode = 'CO' \
#         and i.mutationtype='D' \
#         and a.account_code = refaccountno \
#         and t.ActualDate >= '%(BDATE)s' \
#         and t.ActualDate <= '%(EDATE)s' \
#         %(ADDFILTER2)s  " % qParam
        
  sSQL += " order by ActualDate, BranchName"
  return config.CreateSQL(sSQL).rawresult
    
def PrintReport(helper, config, param):
  global addFilter

  corporate = helper.CreateObject('Corporate')
    
  reportdef = config.HomeDir + 'reports/distributionreport.mtr'
  oReport = textreport.TextReport(reportdef)  
  
  res = GetData(config,param)

  # Set Title
  BranchCode = param.BranchCode
  oBranch = helper.GetObject('Branch', BranchCode)
  Cabang = '%s - %s' % (BranchCode, oBranch.BranchName)
  oReport.SetVars('BRANCH', Cabang)
  
  #IsAll

  #if param.IsAllProduct == 'T':
  #  oReport.SetVars('ACCOUNT', 'SEMUA PRODUK')
  #  currencyCode = str(param.GetFieldByName('LProductAccount.CurrencyCode'))
  #  if currencyCode == None: currencyCode = '000'
  #  oReport.SetVars('CURRENCY', currencyCode)
  #else:
  #  accountNo = param.GetFieldByName('LProductAccount.AccountNo')
  #  accountName = param.GetFieldByName('LProductAccount.AccountName')     
  #  oReport.SetVars('ACCOUNT', '%s-%s' % (accountNo, accountName))
  #  oReport.SetVars('CURRENCY', param.GetFieldByName('LProductAccount.CurrencyCode'))
  
  # Set Date
  aBeginDate = param.BeginDate
  aEndDate = param.EndDate
  
  if aBeginDate == aEndDate:
    Tanggal = '%s' % config.FormatDateTime('dd mmm yyyy', aBeginDate)
  else:    
    Tanggal = '%s s.d. %s' % (
                 config.FormatDateTime('dd mmm yyyy', aBeginDate),
                 config.FormatDateTime('dd mmm yyyy', aEndDate) 
               )
  oReport.SetVars('DATE', Tanggal)

  # Set Total
  TotalAmount = DistributionSummary(config, aBeginDate, aEndDate,addFilter)
  oReport.SetVars('TOTALAMOUNT', config.FormatFloat(',0.00', TotalAmount))

  # Set nama file output.txt
  reportFile = corporate.GetUserHomeDir() + '\\DistributionReport.txt'
  oReport.OpenReport(reportFile)
  
  try:
    
    while not res.Eof:
      aContent = {}
      aDate = res.TransactionDate
      aContent['DATE']        = '%2s-%2s-%4s' % (str(aDate[2]).zfill(2), 
                                                 str(aDate[1]).zfill(2), 
                                                 str(aDate[0]))
      aContent['REFNO']       = res.ReferenceNo
      aContent['ACCOUNT']     = res.AccountName[:24]
      aContent['DESCRIPTION'] = res.Description[:29]

      Amount , Rate, CurrencyName = GetAmount(res)
      
      aContent['CURRENCYNAME'] = CurrencyName
      aContent['RATE']         = config.FormatFloat(',0.00', Rate)
      aContent['AMOUNT']       = config.FormatFloat(',0.00', Amount)
      aContent['EKUIVAMOUNT']  = config.FormatFloat(',0.00', res.EkuivalenAmount)
      aContent['INPUTER']      = res.Inputer
      aContent['AUTHSTATUS']   = res.AuthStatus
      aContent['CHANNEL']      = res.Channel[:20]
      aContent['FUNDENTITY']   = res.FundEntity
      aContent['TRANSNO'] = res.TransactionNo
      
      # Get SponsorName
      SName = res.DonorName or ''
#       oST = helper.GetObject('SponsorTransaction',res.TransactionItemId)
#       if not oST.isnull :
#          SName = oST.LSponsor.Name
      aContent['SPONSORNAME'] = SName[:19]            
      oReport.PrintRow('detail', aContent)
       
      res.Next()
    #-- while
    
  finally:
    oReport.Close()
  
  return reportFile
  
  
def DistributionSummary(config, BeginDate=None, EndDate = None, addFilter=''):
  qParam = {}
  qParam['BDATE'] = config.FormatDateTime('yyyy-mm-dd', BeginDate) 
  qParam['EDATE'] = config.FormatDateTime('yyyy-mm-dd', EndDate) 
  qParam['ADDFILTER'] = addFilter

  sSQL = "\
      select sum(i.Ekuivalenamount) as TotalBalance \
      from accounttransactionitem a, transactionitem i, \
        transaction t, financialaccount f , productaccount p ,branch b\
      where a.TransactionItemId = i.TransactionItemId \
        and i.TransactionId = t.TransactionId \
        and p.AccountNo=f.AccountNo \
        and a.AccountNo = f.AccountNo \
        and f.AccountNo = p.AccountNo \
        and b.branchcode = i.branchcode \
        and t.TransactionCode in ('DD001','CAR','EAR','FA','GT') \
        and t.ActualDate >= '%(BDATE)s' \
        and t.ActualDate <= '%(EDATE)s' \
        and i.MutationType = 'D' \
        %(ADDFILTER)s \
    " % qParam
  
  res = config.CreateSQL(sSQL).rawresult
  Total1 = res.GetFieldValueAt(0) or 0.0  

  sSQL2 = " \
      select sum(i.Ekuivalenamount) \
      from accounttransactionitem a, transactionitem i, \
        transaction t, financialaccount f , productaccount p ,branch b\
      where a.TransactionItemId = i.TransactionItemId \
        and i.TransactionId = t.TransactionId \
        and p.AccountNo=f.AccountNo \
        and a.AccountNo = f.AccountNo \
        and f.AccountNo = p.AccountNo \
        and b.branchcode = i.branchcode \
        and t.TransactionCode in ('CA') \
        and t.ActualDate >= '%(BDATE)s' \
        and t.ActualDate <= '%(EDATE)s' \
        and i.MutationType = 'D' \
        and not exists(select 1 from cashadvancereturninfo c where c.SourceTransactionId=t.TransactionId) \
        %(ADDFILTER)s \
    " % qParam
  
  res = config.CreateSQL(sSQL2).rawresult
  Total2 = res.GetFieldValueAt(0) or 0.0  

  return Total1 + Total2