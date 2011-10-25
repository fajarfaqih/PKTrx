import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.labs.m_textreport as textreport
import os  
import sys
import datetime
import workdays

addFilter = ""
    
def AsString(tdate):
  return ('%s/%s/%s' % (str(tdate[2]), str(tdate[1]), str(tdate[0])))

def DAFScriptMain(config,parameters,returns):
  return 1

def PrintText(config,parameters,returns):
  helper = phelper.PObjectHelper(config)

  param = parameters.FirstRecord
  
  sw = returns.AddStreamWrapper()
  reportFile = GenerateText(helper, config, param)
  
  sw.LoadFromFile(reportFile)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(reportFile)

def PrintExcel(config,parameters,returns):
  helper = phelper.PObjectHelper(config)

  param = parameters.FirstRecord
  
  sw = returns.AddStreamWrapper()
  reportFile = GenerateExcel(helper, config, param)
  
  sw.LoadFromFile(reportFile)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(reportFile)
  
def GetReportData(config,param):
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
                        and sa.donorid=%d and st.transactionid=t.transactionid \
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
      addFilter += " and a.AccountNo='%s' " % param.AccountNo
      addFilter2 += " and false"            

#     if param.IsAllSponsor == 'F' :      
#       addFilter += " and exists ( \
#                         select 1 from sponsortransaction sp \
#                         where sp.transactionitemid = a.transactionitemid \
#                           and sp.SponsorId=%d \
#                      ) " % param.GetFieldByName('LSponsor.SponsorId')                     

    if param.IsAllVolunteer == 'F' :      
      addFilter += " and exists ( \
                        select 1 from volunteertransaction vt \
                        where vt.transactionitemid = a.transactionitemid \
                          and vt.VolunteerId='%s' \
                     ) " % param.GetFieldByName('LVolunteer.VolunteerId')
      addFilter2 += " and false"

    if param.IsAllFundEntity == 'F' :
      addFilter += " and a.FundEntity='%s' " % param.FundEntity
      if param.FundEntity != 4:
        addFilter2 += " and false"

    if param.IsAllMarketer == 'F' :
      addFilter += " and t.MarketerId=%d " % param.GetFieldByName('LMarketer.MarketerId')
    
    qParam = {}
    qParam['BDATE'] = config.FormatDateTime('yyyy-mm-dd', aBeginDate) 
    qParam['EDATE'] = config.FormatDateTime('yyyy-mm-dd', aEndDate) 
    
    #qParam['BRANCH'] = aBranchCode
    qParam['CURRENCY'] = '000'
    qParam['ADDFILTER'] = addFilter
    qParam['ADDFILTER2'] = addFilter2
       
    sSQL = "\
        select t.ActualDate, t.ReferenceNo, f.AccountName, \
          t.Description, i.Amount, i.Rate, i.Ekuivalenamount,i.CurrencyCode, t.Inputer, \
          t.AuthStatus, t.TransactionId, t.donorname, \
          (case when t.ChannelCode = 'R' then 'Kas Cabang' \
                when t.ChannelCode = 'P' then 'Kas Kecil' \
                when t.ChannelCode = 'A' then 'Bank' else 'Aktiva' end) as Channel ,\
          (case when a.FundEntity = '1' then 'Zakat' \
                when a.FundEntity = '2' then 'Infaq' \
                when a.FundEntity = '3' then 'Wakaf' \
                when a.FundEntity = '4' then 'Amil' \
                when a.FundEntity = '5' then 'Lainnya' \
                else '' end) as FundEntity, t.MarketerId ,\
           i.transactionitemid, b.branchname ,t.TransactionNo , \
         t.currencycode as TransCurrencyCode , t.rate as TransRate \
        from accounttransactionitem a, transactionitem i, \
          transaction t, financialaccount f , productaccount p, \
          public.php_donor d, branch b \
        where a.TransactionItemId = i.TransactionItemId \
          and i.TransactionId = t.TransactionId \
          and p.AccountNo = f.AccountNo \
          and a.AccountNo = f.AccountNo \
          and a.DonorId = d.id \
          and b.branchcode = i.branchcode \
          and t.TransactionCode in ('SD001','INVP')  \
          and t.ActualDate >= '%(BDATE)s' \
          and t.ActualDate <= '%(EDATE)s' \
          and i.MutationType='C' \
          %(ADDFILTER)s \
      " % qParam

#     sSQL += " union \
#       select t.ActualDate, t.ReferenceNo, a.account_name as AccountName, \
#         t.Description, i.Amount, i.Rate, i.Ekuivalenamount, i.CurrencyCode, t.Inputer, \
#         t.AuthStatus, t.TransactionId, '' as donorname, \
#         (case when t.ChannelCode = 'R' then 'Kas Cabang' \
#               when t.ChannelCode = 'P' then 'Kas Kecil' \
#               when t.ChannelCode = 'A' then 'Bank' else 'Aktiva' end) as Channel , \
#         'Amil' as FundEntity, t.MarketerId ,\
#          i.transactionitemid , b.branchname, t.TransactionNo , \
#          t.currencycode as TransCurrencyCode , t.rate as TransRate \
#       from transaction.transaction t, transaction.transactionitem i, \
#         accounting.account a , branch b \
#       where t.transactionid = i.transactionid \
#         and t.transactioncode = 'CI' \
#         and i.mutationtype='C' \
#         and a.account_code = refaccountno \
#         and b.branchcode = i.branchcode \
#         and t.ActualDate >= '%(BDATE)s' \
#         and t.ActualDate <= '%(EDATE)s' \
#         %(ADDFILTER2)s  " % qParam
        
    sSQL += " order by ActualDate, BranchName,TransactionId"
   
    return config.CreateSQL(sSQL).rawresult

        
def GenerateExcel(helper, config, param):
  # Get Info Cabang
  corporate = helper.CreateObject('Corporate')
  BranchCode = config.SecurityContext.GetUserInfo()[4]
  CabangInfo = corporate.GetCabangInfo(BranchCode)
  Cabang = '%s - %s' % (BranchCode,CabangInfo.Nama_Cabang)

  aBeginDate = param.BeginDate
  aEndDate = param.EndDate
    
  if aBeginDate == aEndDate:
     Tanggal = '%s' % config.FormatDateTime('dd mmm yyyy', aBeginDate)
  else:    
     Tanggal = '%s - %s' % (
                 config.FormatDateTime('dd mm yyyy', aBeginDate),
                 config.FormatDateTime('dd mm yyyy', aEndDate) 
               ) 
  # end if  
  
  # Prepare Excel Object
  PrintHelper = helper.CreateObject('PrintHelper')
  workbook = PrintHelper.LoadExcelTemplate('CollectionReport')
  FullFileName = ''
  
  try :                 
    workbook.ActivateWorksheet('data')

    workbook.SetCellValue(2, 3, Cabang)
    workbook.SetCellValue(3, 3, Tanggal)
    
    ds = GetReportData(config, param)
    row = 7
    TotalTransaksi = 0
    while not ds.Eof:
      workbook.SetCellValue(row, 1, str(row - 5) )
      workbook.SetCellValue(row, 2, AsString(ds.ActualDate))
      workbook.SetCellValue(row, 3, ds.DonorName)
      workbook.SetCellValue(row, 4, ds.AccountName)
      workbook.SetCellValue(row, 5, ds.Description)
      workbook.SetCellValue(row, 6, ds.Channel)
      workbook.SetCellValue(row, 7, ds.Amount)
      workbook.SetCellValue(row, 8, ds.FundEntity)      
            
      TotalTransaksi += ds.Amount      
      # Get VolunteerName
      VName = ''        
      oVT = helper.GetObject('VolunteerTransaction',ds.TransactionItemId)
      if not oVT.isnull :
         VName = oVT.LVolunteer.VolunteerName
      workbook.SetCellValue(row, 9, VName)
      
      # Get SponsorName
      SName = ''
#       oST = helper.GetObject('SponsorTransaction',ds.TransactionItemId)
#       if not oST.isnull :
#          oDonor = helper.CreateObject('ExtDonor')
#          oDonor.GetData(oST.SponsorId)
#          SName = oDonor.full_name
      
      workbook.SetCellValue(row, 10, SName)      
      workbook.SetCellValue(row, 11, ds.ReferenceNo)
      workbook.SetCellValue(row, 12, ds.Inputer)
      
      row += 1
      ds.Next()
    # end while
    workbook.SetCellValue(4, 3, TotalTransaksi)
    
    # save report file
    FileName = 'CollectionReport.xls'
    
    FullFileName = corporate.GetUserHomeDir() + '\\' + FileName
    if os.access(FullFileName, os.F_OK) == 1:
        os.remove(FullFileName)
    workbook.SaveAs(FullFileName)
    
  finally:
    workbook = None
  # try except
    
  return FullFileName
  #-- while

def GenerateText(helper, config, param):
  # Get Info Cabang     
  corporate = helper.CreateObject('Corporate')             
  reportdef = config.HomeDir + 'reports/collectionreport.mtr'
  oReport = textreport.TextReport(reportdef)  
  
  # Set Title
  oReport.SetVars('BRANCH', param.BranchCode)
  
  aBeginDate = param.BeginDate
  aEndDate = param.EndDate
  oReport.SetVars('BDATE', config.FormatDateTime('dd-mm-yyyy', aBeginDate))
  oReport.SetVars('EDATE', config.FormatDateTime('dd-mm-yyyy', aEndDate))
  
  # Set nama file output.txt
  reportFile = corporate.GetUserHomeDir() + '\\CollectionReport.txt'
  oReport.OpenReport(reportFile)
  
  try:
    
    res = GetReportData(config, param)
    
    while not res.Eof:
      aContent = {}
      aDate = res.ActualDate
      aContent['DATE']        = '%2s-%2s-%4s' % (str(aDate[2]).zfill(2), 
                                                 str(aDate[1]).zfill(2), 
                                                 str(aDate[0]))
      aContent['REFNO']       = res.ReferenceNo
      aContent['ACCOUNT']     = res.AccountName
      aContent['DESCRIPTION'] = res.Description
      aContent['AMOUNT']      = config.FormatFloat(',0.00', res.EkuivalenAmount)
      aContent['INPUTER']     = res.Inputer
      aContent['AUTHSTATUS']  = res.AuthStatus
      aContent['NAMADONOR']  = res.DonorName[:20]
      aContent['CHANNEL']  = res.Channel[:20]
      aContent['FUNDENTITY'] = res.FundEntity
      
      # Get VolunteerName
      VName = ''
      oVT = helper.GetObject('VolunteerTransaction',res.TransactionItemId)
      if not oVT.isnull :
         VName = oVT.LVolunteer.VolunteerName
      aContent['VOLUNTEERNAME'] = VName[:19]
      
      # Get SponsorName
      SName = ''
#       oST = helper.GetObject('SponsorTransaction',res.TransactionItemId)
#       if not oST.isnull :
#          oDonor = helper.CreateObject('ExtDonor')
#          oDonor.GetData(oST.SponsorId)
#          SName = oDonor.full_name
#          #SName = oST.LSponsor.Name
         
      aContent['SPONSORNAME'] = SName[:19]
      
      
      oReport.PrintRow('detail', aContent)       
      res.Next()
    #-- while
    
  finally:
    oReport.Close()

  return reportFile 
  
def CreateCurrencyDict(config):
  sql = "select * from currency"
  
  resCurr = config.CreateSQL(sql).rawresult
  
  dictCurr = {}
  while not resCurr.Eof :
    dictCurr[resCurr.Currency_Code] = resCurr.Short_Name
    resCurr.Next()
  
  return dictCurr
    
def GetDataTransaction(config,parameters,returns):
  global addFilter
  
  helper = phelper.PObjectHelper(config)
  CURRSYMBOL = CreateCurrencyDict(config)
  
  param = parameters.FirstRecord
  
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['Cabang',''],
    ['Tanggal',''],
    ['TotalAmount',0.0],
    ['ZakatBalance',0.0],
    ['InfaqBalance',0.0],
    ['WakafBalance',0.0],
    ['AmilBalance',0.0],
    ['OtherBalance',0.0],
    ['WorkDays',0],    
  )
  
  dsData = returns.AddNewDatasetEx(
    'ReportData',
    ';'.join([
      'TransactionDate: datetime',
      'TransactionDateStr: string',
      'ReferenceNo: string',      
      'AccountName: string',
      'Description: string',
      'Amount: float',
      'CurrencyCode: string',
      'Rate: float',
      'EkuivalenAmount: float',                  
      'AuthStatus: string',
      'Channel:string',
      'FundEntity: string',
      'SponsorName: string',
      'VolunteerName: string',      
      'Inputer: string',
      'Marketer: string',
      'BranchName: string',
      'TransactionNo: string',      
    ])
  )
  
  try:
    corporate = helper.CreateObject('Corporate')
    BranchCode = None
    Cabang = '' 
    if param.IsAllBranch == 'F' :
      BranchCode = param.GetFieldByName('LBranch.BranchCode') #config.SecurityContext.GetUserInfo()[4]
      CabangInfo = corporate.GetCabangInfo(BranchCode)
      Cabang = '%s - %s' % (BranchCode,CabangInfo.Nama_Cabang)
  
    aBeginDate = param.BeginDate
    aEndDate = param.EndDate
      
    if aBeginDate == aEndDate:
       Tanggal = '%s' % config.FormatDateTime('dd mmm yyyy', aBeginDate)
    else:    
       Tanggal = '%s s.d. %s' % (
                   config.FormatDateTime('dd mmm yyyy', aBeginDate),
                   config.FormatDateTime('dd mmm yyyy', aEndDate) 
                 )
                 
    res = GetReportData(config, param)
    
    MarketerList = {}
    TotalAmount = 0.0
    while not res.Eof:
      recData = dsData.AddRecord()
      aDate = res.ActualDate
      recData.TransactionDateStr = '%2s-%2s-%4s' % (str(aDate[2]).zfill(2), 
                                                 str(aDate[1]).zfill(2), 
                                                 str(aDate[0]))
      recData.ReferenceNo = res.ReferenceNo
      recData.AccountName = res.AccountName
      recData.Description = res.Description

      if res.CurrencyCode != res.TransCurrencyCode and res.CurrencyCode == '000':
        recData.CurrencyCode = CURRSYMBOL[res.TransCurrencyCode]
        recData.Rate = res.TransRate
        recData.Amount      = res.Amount / res.TransRate
      else :
        recData.CurrencyCode = CURRSYMBOL[res.CurrencyCode]
        recData.Rate = res.Rate
        recData.Amount      = res.Amount
      # end if

      recData.EkuivalenAmount = res.EkuivalenAmount
      recData.Inputer     = res.Inputer
      recData.AuthStatus  = res.AuthStatus
      recData.SponsorName = res.DonorName
      recData.Channel     = res.Channel
      recData.Fundentity  = res.FundEntity
      recData.BranchName  = res.BranchName
      recData.TransactionNo = res.TransactionNo
      
      TotalAmount += res.EkuivalenAmount
      # Get VolunteerName
      VName = ''
      oVT = helper.GetObject('VolunteerTransaction',res.TransactionItemId)
      if not oVT.isnull :
         VName = oVT.LVolunteer.VolunteerName
      recData.VolunteerName = VName
      
      
      # Get SponsorName
      SName = res.DonorName or ''
#       oST = helper.GetObject('SponsorTransaction',res.TransactionItemId)
#       if not oST.isnull :
#          oDonor = helper.CreateObject('ExtDonor')
#          oDonor.GetData(oST.SponsorId)
#          SName = oDonor.full_name
#          #SName = oST.LSponsor.Name         
      recData.SponsorName = SName
      # Get MarketerName
      recData.Marketer = ''
      if res.MarketerId not in [0,'',None]:
        if MarketerList.has_key(res.MarketerId):
          recData.Marketer = MarketerList[res.MarketerId]
        else:
          oMarketer = helper.GetObject('Marketer',res.MarketerId)
          if not oMarketer.isnull :
            recData.Marketer = oMarketer.Full_Name
            MarketerList[oMarketer.MarketerId] = oMarketer.Full_Name        
        
      res.Next()
    #-- while
    
    # Get Balance
    
    status.ZakatBalance = FundEntityBalance(config,BranchCode,aBeginDate,1,addFilter)    
    status.InfaqBalance = FundEntityBalance(config,BranchCode,aBeginDate,2,addFilter)
    status.WakafBalance = FundEntityBalance(config,BranchCode,aBeginDate,3,addFilter)
    status.AmilBalance = FundEntityBalance(config,BranchCode,aBeginDate,4,addFilter) #+ AmilBalance(config,BranchCode,aBeginDate,addFilter)   
    status.OtherBalance = FundEntityBalance(config,BranchCode,aBeginDate,5,addFilter)
      
    status.TotalAmount = TotalAmount
    status.Cabang = Cabang
    status.Tanggal = Tanggal
    sY,sM,sD = config.ModLibUtils.DecodeDate(aBeginDate)[:3]    
    eY,eM,eD = config.ModLibUtils.DecodeDate(aEndDate)[:3]
    status.WorkDays = workdays.networkdays(
                 datetime.date(sY,sM,sD),
                 datetime.date(eY,eM,eD)
                 )
    
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

def FundEntityBalance(config,Branch=None,Date=None, FundEntity=1,addFilter=''):  
  if Date == None :
    Date = int(config.Now())

  aDate = config.FormatDateTime('yyyy-mm-dd', Date)
    
  param = {}
  param['FUNDENTITY'] = str(FundEntity)
  param['DATE'] = aDate
  
  sSQL ="\
    select \
    	sum(i.ekuivalenamount) as BeginBalance \
    from transactionitem i, accounttransactionitem a, transaction t , branch b\
    where i.transactionitemid = a.transactionitemid \
      and i.transactionid = t.transactionid \
      and a.FundEntity = %(FUNDENTITY)s \
      and t.actualdate < '%(DATE)s' \
      and i.mutationtype = 'C' \
      and b.branchcode = i.branchcode \
      and t.TransactionCode in ('SD001','INVP')  \
  " % param 
  
  res = config.CreateSQL(sSQL + addFilter).rawresult
  
  return res.GetFieldValueAt(0) or 0.0

def AmilBalance(config,Branch=None,Date=None,addFilter=''):  
  if Date == None :
    Date = int(config.Now())

  aDate = config.FormatDateTime('yyyy-mm-dd', Date)
    
  param = {}
  param['DATE'] = aDate
  
  sSQL ="\
    select \
    	sum(i.ekuivalenamount) as BeginBalance \
    from transactionitem i, accounttransactionitem a, transaction t , branch b \
    where i.transactionitemid = a.transactionitemid \
      and i.transactionid = t.transactionid \
      and t.transactioncode in ('CI') \
      and t.actualdate < '%(DATE)s' \
      and i.mutationtype = 'C' \
      and b.branchcode = i.branchcode \
  " % param 
  
  res = config.CreateSQL(sSQL + addFilter).rawresult
  
  return res.GetFieldValueAt(0) or 0.0
