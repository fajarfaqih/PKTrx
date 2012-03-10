import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormSetDataEx(uideflist, parameter) :
  config = uideflist.Config
  rec = uideflist.uipData.Dataset.AddRecord()
  rec.UserBranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.UserBranchName = str(config.SecurityContext.GetUserInfo()[5])
  rec.HeadOfficeCode = config.SysVarIntf.GetStringSysVar('OPTION','HeadOfficeCode')

  Now = config.Now()

  y = config.ModLibUtils.DecodeDate(Now)[0]
  rec.BeginDate = config.ModLibUtils.EncodeDate(y,1,1)
  rec.EndDate = int(Now)


def SummaryEmpAr(config,params,returns):
  status = returns.CreateValues(
     ['Is_Err',0],['Err_Message',''],
     ['PeriodStr',''],['BranchName',''],
     ['BeginDateStr',''],['EndDateStr',''],
     ['BeginBalance',0.0],
     ['TotalDebet',0.0],
     ['TotalCredit',0.0],
     ['EndBalance',0.0],
  )
  
  param = params.FirstRecord
  BranchCode = param.GetFieldByName('LBranch.BranchCode')
  IsAllBranch = param.IsAllBranch
  BeginDate = param.BeginDate
  EndDate = param.EndDate
  UserBranchCode = param.UserBranchCode
  HeadOfficeCode = param.HeadOfficeCode
  MasterBranchCode = param.MasterBranchCode
  
  try:
    helper = phelper.PObjectHelper(config)
    
    # Set BranchName
    if BranchCode not in ['',None] :
      corporate = helper.CreateObject('Corporate')
      CabangInfo = corporate.GetCabangInfo(BranchCode)

      status.BranchName = CabangInfo.Nama_Cabang
      
    # Set strPeriod
    status.BeginDateStr = config.FormatDateTime('dd-mm-yyyy',BeginDate)
    status.EndDateStr = config.FormatDateTime('dd-mm-yyyy',EndDate)
    if BeginDate == EndDate :
      status.PeriodStr = config.FormatDateTime('dd-mm-yyyy',BeginDate)
    else:
      status.PeriodStr = "%s s/d %s" % (
                   config.FormatDateTime('dd-mm-yyyy',BeginDate),
                   config.FormatDateTime('dd-mm-yyyy',EndDate)
                 )
    # end if
    
    dsSummary = returns.AddNewDatasetEx(
     'summary',
     ';'.join([
       'NomorKaryawan: string',
       'NamaKaryawan: string',
       'BranchCode: string',
       'BranchName: string',
       'Debet: float',
       'Kredit: float',
       'TotalMutasi: float',
       'SaldoAwal: float',
       'SaldoAkhir: float'
     ])
    )


    # Set BranchCodeParam
    BranchCodeParam = ''
    if IsAllBranch == 'F' :
      BranchCodeParam = " and a.branchcode='%s' " % BranchCode
    else:
      IsHeadOffice = (UserBranchCode == HeadOfficeCode)

      # Jika Bukan Kantor Pusat maka branchcode dari user login ditambah konsolidasi dengan KCPnya
      if not IsHeadOffice :
        BranchCodeParam = "and ( br.BranchCode='%(BranchCode)s'  \
                           or br.MasterBranchCode='%(BranchCode)s' ) " \
                           % {'BranchCode' : UserBranchCode}

      #end if
    # end if
    
    strSQL = " \
              select a.accountno,a.accountname, a.branchcode, br.branchname, \
                 (select sum(case when d.mutationtype='D' then d.Amount \
                           else -d.Amount \
                      end) \
                     from transaction c, transactionitem d, accounttransactionitem e\
                     where c.transactionid=d.transactionid \
                        and d.transactionitemid=e.transactionitemid \
                        and e.accountno = a.accountno) as BeginBalance, \
                 (select sum(d.Amount) \
                     from transaction.transaction c, \
                          transaction.transactionitem d, \
                          transaction.accounttransactionitem e \
                     where c.transactionid = d.transactionid and d.transactionitemid = e.transactionitemid \
                         and c.actualdate between '%(BEGINDATE)s' and '%(ENDDATE)s'  and e.accountno=a.accountno \
                         and d.mutationtype='D') as Debet, \
                 (select sum(d.Amount) \
                     from transaction.transaction c, \
                          transaction.transactionitem d, \
                          transaction.accounttransactionitem e \
                     where c.transactionid = d.transactionid and d.transactionitemid = e.transactionitemid \
                         and c.actualdate between '%(BEGINDATE)s' and '%(ENDDATE)s'  and e.accountno=a.accountno \
                         and d.mutationtype='C') as Kredit \
              from transaction.financialaccount a, transaction.accountreceivable b, branch br \
              where a.accountno=b.accountno \
                  and b.AccountReceivableType = 'E' \
                  and a.BranchCode = br.BranchCode \
                  %(BRANCHCODEPARAM)s \
                 order by  a.branchcode, a.accountname \
                " % {
                  'BRANCHCODEPARAM' : BranchCodeParam ,
                  'BEGINDATE' : config.FormatDateTime('yyyy-mm-dd',BeginDate),
                  'ENDDATE' : config.FormatDateTime('yyyy-mm-dd',EndDate)
               }

    res = config.CreateSQL(strSQL).RawResult

    while not res.Eof:
      recSum = dsSummary.AddRecord()
      recSum.NomorKaryawan = res.AccountNo
      recSum.NamaKaryawan = res.AccountName
      recSum.BranchCode = res.BranchCode
      recSum.BranchName = res.BranchName
      
      recSum.Debet = res.Debet or 0.0
      recSum.Kredit = res.Kredit or 0.0
      recSum.TotalMutasi = (res.Debet or 0.0 ) - ( res.Kredit or 0.0)
      
      #AccountR = helper.GetObject('AccountReceivable',res.AccountNo)
      #SaldoAwal = AccountR.GetBalanceByDate(BeginDate)
      SaldoAwal = res.BeginBalance
      recSum.SaldoAwal = SaldoAwal
      recSum.SaldoAkhir = SaldoAwal + recSum.TotalMutasi
      
      status.BeginBalance += recSum.SaldoAwal
      status.TotalDebet += recSum.Debet
      status.TotalCredit += recSum.Kredit
      status.EndBalance += recSum.SaldoAkhir
      
      res.Next()
      
    # end while
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
