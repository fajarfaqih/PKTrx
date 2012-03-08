import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormSetDataEx(uideflist, parameter) :
  config = uideflist.Config
  rec = uideflist.uipData.Dataset.AddRecord()
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.BranchName = str(config.SecurityContext.GetUserInfo()[5])
  rec.HeadOfficeCode = config.SysVarIntf.GetStringSysVar('OPTION','HeadOfficeCode')

  Now = config.Now()

  y = config.ModLibUtils.DecodeDate(Now)[0]
  rec.BeginDate = config.ModLibUtils.EncodeDate(y,1,1)
  rec.EndDate = int(Now)


def AsDateTime(config,tdate):
  utils = config.ModLibUtils
  return utils.EncodeDate(tdate[0], tdate[1], tdate[2])


def SummaryInvestment(config,params,returns):
  status = returns.CreateValues(
     ['Is_Err',0],['Err_Message',''],
     ['PeriodStr',''],['BranchName',''],
     ['BeginDateStr',''],['EndDateStr',''],
     ['BeginBalance',0.0],
     ['TotalDebet',0.0],
     ['TotalCredit',0.0],
     ['EndBalance',0.0],
     ['TotalDebetHist',0.0],
     ['TotalCreditHist',0.0],
  )
  
  BranchCode = params.FirstRecord.BranchCode
  BeginDate = params.FirstRecord.BeginDate
  EndDate = params.FirstRecord.EndDate
  
  try:
    helper = phelper.PObjectHelper(config)
    
    corporate = helper.CreateObject('Corporate')
    CabangInfo = corporate.GetCabangInfo(BranchCode)

    status.BranchName = CabangInfo.Nama_Cabang
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
       'Debet: float',
       'Kredit: float',
       'TotalMutasi: float',
       'SaldoAwal: float',
       'SaldoAkhir: float',
       'CurrencyName: string'
     ])
    )


    LsSQL = []
    strSQLEmp = " \
              select ve.employeeid as investeeid, ve.employeename as investeename, a.currencycode, c.short_name, \
              ( select sum(case when d.mutationtype='D' then d.Amount \
                           else -d.Amount \
                      end) \
              from transactionitem d, transaction e, accounttransactionitem f\
              where d.transactionid=e.transactionid \
                 and d.transactionitemid=f.transactionitemid \
                 and f.accountno = a.accountno and e.actualdate < '%(BEGINDATE)s' ) as BeginBalance, \
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
              from transaction.financialaccount a, transaction.accountreceivable b, \
                   transaction.currency c,  transaction.investment i, transaction.vemployee ve \
              where a.accountno = b.accountno \
                  and i.accountno = b.accountno \
                  and ve.employeeid = i.employeeid \
                  and a.currencycode = c.currency_code \
                  and b.AccountReceivableType = 'I' \
                  and a.branchcode = '%(BRANCHCODE)s' \
                 order by  b.employeeidnumber \
                " % {
                  'BRANCHCODE' : BranchCode ,
                  'BEGINDATE' : config.FormatDateTime('yyyy-mm-dd',BeginDate),
                  'ENDDATE' : config.FormatDateTime('yyyy-mm-dd',EndDate)
               }

    LsSQL.append(strSQLEmp)
    
    strSQLExt = " \
              select ve.investeeid, ve.investeename , a.currencycode, c.short_name, \
              ( select sum(case when d.mutationtype='D' then d.Amount \
                           else -d.Amount \
                      end) \
              from transactionitem d, transaction e, accounttransactionitem f\
              where d.transactionid=e.transactionid \
                 and d.transactionitemid=f.transactionitemid \
                 and f.accountno = a.accountno and e.actualdate < '%(BEGINDATE)s' ) as BeginBalance, \
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
              from transaction.financialaccount a, transaction.accountreceivable b, \
                   transaction.currency c,  transaction.investment i, transaction.investee ve \
              where a.accountno = b.accountno \
                  and i.accountno = b.accountno \
                  and ve.investeeid = i.investeeid \
                  and a.currencycode = c.currency_code \
                  and b.AccountReceivableType = 'I' \
                  and a.branchcode = '%(BRANCHCODE)s' \
                 order by  b.employeeidnumber \
                " % {
                  'BRANCHCODE' : BranchCode ,
                  'BEGINDATE' : config.FormatDateTime('yyyy-mm-dd',BeginDate),
                  'ENDDATE' : config.FormatDateTime('yyyy-mm-dd',EndDate)
               }

    LsSQL.append(strSQLExt)
    
    for strSQL in LsSQL :
      res = config.CreateSQL(strSQL).RawResult

      res.First()
      while not res.Eof:
        recSum = dsSummary.AddRecord()
        #recSum.NomorKaryawan = res.AccountNo
        recSum.NomorKaryawan = str(res.investeeid)
        recSum.NamaKaryawan = res.investeename
        recSum.CurrencyName = res.Short_Name
        recSum.Debet = res.Debet or 0.0
        recSum.Kredit = res.Kredit or 0.0
        recSum.TotalMutasi = (res.Debet or 0.0 ) - ( res.Kredit or 0.0)

        #AccountR = helper.GetObject('AccountReceivable',res.AccountNo)
        SaldoAwal = res.BeginBalance or 0.0 #AccountR.GetBalanceByDate(BeginDate)

        recSum.SaldoAwal = SaldoAwal
        recSum.SaldoAkhir = SaldoAwal + recSum.TotalMutasi

        status.BeginBalance += recSum.SaldoAwal
        status.TotalDebet += recSum.Debet
        status.TotalCredit += recSum.Kredit
        status.EndBalance += recSum.SaldoAkhir

        res.Next()

      # end while
    
    
    #--- GET HISTORI TRANSAKSI
    dsHist = returns.AddNewDatasetEx(
      'historitransaksi',
      ';'.join([
        'TransactionItemId: integer',
        'TransactionDate: datetime',
        'TransactionDateStr: string',
        'TransactionCode: string',
        'MutationType: string',
        'Amount: float',
        'AmountEkuivalen: float',
        'CurrencyName: string',
        'Rate: float',
        'Debet: float',
        'Kredit: float',
        'ReferenceNo: string',
        'Description: string',
        'Inputer: string',
        'TransactionNo:string',
        'Total:float',
        'AuthStatus:string',
        'AccountName:string',
      ])
    )

    s = ' \
      SELECT FROM InvestmentTransactItem \
      [ \
        LTransaction.ActualDate >= :BeginDate and \
        LTransaction.ActualDate < :EndDate and \
        BranchCode = :BranchCode \
      ] \
      ( \
        TransactionItemId, \
        LTransaction.TransactionDate , \
        LTransaction.TransactionCode , \
        LTransaction.ActualDate , \
        MutationType , \
        Amount , \
        EkuivalenAmount , \
        LTransaction.ReferenceNo , \
        LTransaction.Description , \
        LTransaction.Inputer , \
        LTransaction.TransactionNo ,\
        LTransaction.AuthStatus ,\
        CurrencyCode , \
        Rate , \
        LCurrency.Short_Name , \
        LTransaction.CurrencyCode as TransCurrencyCode , \
        LTransaction.Rate as TransRate , \
        LTransaction.LCurrency.Short_Name as TransCurrencyName , \
        LInvestment.AccountName, \
        Self \
      ) \
      THEN ORDER BY ASC ActualDate, ASC TransactionItemId;'

    oql = config.OQLEngine.CreateOQL(s)
    oql.SetParameterValueByName('BeginDate', BeginDate)
    oql.SetParameterValueByName('EndDate', EndDate + 1)
    oql.SetParameterValueByName('BranchCode', BranchCode)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult

    stAuth = {'T':'Sudah Otorisasi','F':'Belum Otorisasi'}
    while not ds.Eof:
      recHist = dsHist.AddRecord()
      recHist.TransactionItemId = ds.TransactionItemId
      recHist.TransactionDate = AsDateTime(config, ds.ActualDate)
      recHist.TransactionDateStr = config.FormatDateTime('dd-mmm-yyyy',recHist.TransactionDate)
      recHist.TransactionCode = ds.TransactionCode
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
      recHist.AmountEkuivalen = ds.EkuivalenAmount
      recHist.Rate = Rate
      recHist.CurrencyName = TranCurrencyName

      if ds.MutationType == 'D' :
        recHist.Debet = ds.EkuivalenAmount
        #recSaldo.TotalBalance += ds.EkuivalenAmount
        status.TotalDebetHist += ds.EkuivalenAmount
      else:
        recHist.Kredit = ds.EkuivalenAmount
        #recSaldo.TotalBalance -= ds.EkuivalenAmount
        status.TotalCreditHist += ds.EkuivalenAmount
      # endif

      recHist.ReferenceNo = ds.ReferenceNo
      recHist.Description = ds.Description
      recHist.Inputer = ds.Inputer
      recHist.TransactionNo = ds.TransactionNo
      recHist.AccountName = ds.AccountName
      recHist.AuthStatus = stAuth[ds.AuthStatus]

      ds.Next()
    #-- while
    
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
